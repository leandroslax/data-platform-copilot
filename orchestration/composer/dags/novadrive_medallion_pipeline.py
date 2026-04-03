import json
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCheckOperator,
    BigQueryInsertJobOperator,
)
from airflow.providers.postgres.hooks.postgres import PostgresHook
from google.cloud import bigquery
import pendulum
from psycopg2.extras import RealDictCursor


PROJECT_ID = Variable.get("gcp_project_id", default_var="data-platform-copilot-dev")
BRONZE_BUCKET = Variable.get(
    "novadrive_bronze_bucket",
    default_var="data-platform-copilot-dev-data-platform-copilot-bronze",
)
BRONZE_DATASET = Variable.get("novadrive_bronze_dataset", default_var="bronze_novadrive")
SILVER_DATASET = Variable.get("novadrive_silver_dataset", default_var="silver_novadrive")
GOLD_DATASET = Variable.get("novadrive_gold_dataset", default_var="gold_novadrive")
POSTGRES_CONN_ID = Variable.get("novadrive_postgres_conn_id", default_var="novadrive_postgres")
CHECKPOINT_OBJECT = Variable.get(
    "novadrive_checkpoint_object",
    default_var="novadrive/_control/checkpoints.json",
)
BRONZE_LOAD_STATE_OBJECT = Variable.get(
    "novadrive_bronze_load_state_object",
    default_var="novadrive/_control/bronze_load_state.json",
)

TABLES = [
    "cidades",
    "clientes",
    "concessionarias",
    "estados",
    "veiculos",
    "vendas",
    "vendedores",
]

SQL_DIR = Path(__file__).resolve().parent / "sql"
LOCAL_TIMEZONE = pendulum.timezone("America/Sao_Paulo")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def normalize_rows(rows: list[dict[str, Any]], table: str, extracted_at: str) -> list[dict[str, Any]]:
    normalized = []
    for row in rows:
        item = {key: serialize_value(value) for key, value in row.items()}
        item["source_system"] = "novadrive_postgres"
        item["source_table"] = table
        item["ingested_at"] = extracted_at
        normalized.append(item)
    return normalized


def to_ndjson(rows: list[dict[str, Any]]) -> str:
    return "\n".join(json.dumps(row, ensure_ascii=True) for row in rows)


def load_json_from_gcs(object_name: str) -> dict[str, Any]:
    hook = GCSHook()
    if not hook.exists(bucket_name=BRONZE_BUCKET, object_name=object_name):
        return {}

    payload = hook.download(bucket_name=BRONZE_BUCKET, object_name=object_name)
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")
    return json.loads(payload)


def save_json_to_gcs(object_name: str, payload: dict[str, Any]) -> None:
    hook = GCSHook()
    hook.upload(
        bucket_name=BRONZE_BUCKET,
        object_name=object_name,
        data=json.dumps(payload, indent=2, sort_keys=True),
        mime_type="application/json",
    )


def load_checkpoints() -> dict[str, str]:
    return load_json_from_gcs(CHECKPOINT_OBJECT)


def save_checkpoints(checkpoints: dict[str, str]) -> None:
    save_json_to_gcs(CHECKPOINT_OBJECT, checkpoints)


def extract_postgres_to_gcs(**_: Any) -> None:
    checkpoints = load_checkpoints()
    extracted_at = utc_now()
    extracted_at_iso = extracted_at.isoformat()
    updated_checkpoints = dict(checkpoints)

    postgres = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    gcs = GCSHook()

    with postgres.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for table in TABLES:
                checkpoint = checkpoints.get(table)
                if checkpoint:
                    cur.execute(
                        f"""
                        SELECT *
                        FROM public.{table}
                        WHERE COALESCE(data_atualizacao, data_inclusao) > %s
                        ORDER BY COALESCE(data_atualizacao, data_inclusao), 1
                        """,
                        (checkpoint,),
                    )
                else:
                    cur.execute(f"SELECT * FROM public.{table}")

                rows = [dict(row) for row in cur.fetchall()]
                if not rows:
                    logging.info("[%s] no incremental rows found", table)
                    continue

                payload = to_ndjson(normalize_rows(rows, table, extracted_at_iso))
                object_name = (
                    f"novadrive/{table}/extract_date={extracted_at.strftime('%Y-%m-%d')}/"
                    f"extract_hour={extracted_at.strftime('%H')}/"
                    f"part-{extracted_at.strftime('%Y%m%dT%H%M%S')}.jsonl"
                )

                gcs.upload(
                    bucket_name=BRONZE_BUCKET,
                    object_name=object_name,
                    data=payload,
                    mime_type="application/x-ndjson",
                )
                updated_checkpoints[table] = extracted_at_iso
                logging.info("[%s] uploaded %s rows to gs://%s/%s", table, len(rows), BRONZE_BUCKET, object_name)

    save_checkpoints(updated_checkpoints)


def list_gcs_objects(bucket_name: str, table_name: str) -> list[str]:
    hook = GCSHook()
    return sorted(
        object_name
        for object_name in hook.list(bucket_name=bucket_name, prefix=f"novadrive/{table_name}/")
        if object_name.endswith(".jsonl")
    )


def load_bronze_to_bigquery(**_: Any) -> None:
    client = bigquery.Client(project=PROJECT_ID)
    load_state = load_json_from_gcs(BRONZE_LOAD_STATE_OBJECT)
    updated_load_state = dict(load_state)

    for table in TABLES:
        object_names = list_gcs_objects(BRONZE_BUCKET, table)
        if not object_names:
            logging.info("[%s] no .jsonl files found in GCS", table)
            continue

        last_loaded_object = load_state.get(table)
        pending_objects = [object_name for object_name in object_names if last_loaded_object is None or object_name > last_loaded_object]
        if not pending_objects:
            logging.info("[%s] no new files to load into BigQuery", table)
            continue

        uris = [f"gs://{BRONZE_BUCKET}/{object_name}" for object_name in pending_objects]
        table_id = f"{PROJECT_ID}.{BRONZE_DATASET}.{table}_raw"
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
        )

        load_job = client.load_table_from_uri(uris, table_id, job_config=job_config)
        load_job.result()
        updated_load_state[table] = pending_objects[-1]
        logging.info("[%s] loaded %s new files into %s", table, len(uris), table_id)

    save_json_to_gcs(BRONZE_LOAD_STATE_OBJECT, updated_load_state)


def read_sql(filename: str) -> str:
    sql_path = SQL_DIR / filename
    if not sql_path.exists():
        raise AirflowException(f"SQL file not found: {sql_path}")
    return sql_path.read_text()


default_args = {
    "owner": "data-platform",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="novadrive_medallion_pipeline",
    description="Incremental ingestion and medallion modeling for Novadrive in GCP.",
    default_args=default_args,
    start_date=datetime(2026, 3, 30, tzinfo=LOCAL_TIMEZONE),
    schedule="0 * * * *",
    catchup=False,
    max_active_runs=1,
    tags=["novadrive", "medallion", "composer"],
) as dag:
    extract_postgres_to_gcs_bronze = PythonOperator(
        task_id="extract_postgres_to_gcs_bronze",
        python_callable=extract_postgres_to_gcs,
    )

    load_gcs_to_bigquery_bronze = PythonOperator(
        task_id="load_gcs_to_bigquery_bronze",
        python_callable=load_bronze_to_bigquery,
    )

    build_silver_vendas = BigQueryInsertJobOperator(
        task_id="build_silver_vendas",
        configuration={
            "query": {
                "query": read_sql("01_silver_vendas.sql"),
                "useLegacySql": False,
            }
        },
        location="US",
        project_id=PROJECT_ID,
    )

    build_gold_faturamento = BigQueryInsertJobOperator(
        task_id="build_gold_faturamento_por_concessionaria",
        configuration={
            "query": {
                "query": read_sql("02_gold_faturamento_por_concessionaria.sql"),
                "useLegacySql": False,
            }
        },
        location="US",
        project_id=PROJECT_ID,
    )

    build_gold_vendedores = BigQueryInsertJobOperator(
        task_id="build_gold_performance_vendedores",
        configuration={
            "query": {
                "query": read_sql("03_gold_performance_vendedores.sql"),
                "useLegacySql": False,
            }
        },
        location="US",
        project_id=PROJECT_ID,
    )

    build_ml_receita_diaria = BigQueryInsertJobOperator(
        task_id="build_ml_receita_diaria_concessionarias",
        configuration={
            "query": {
                "query": read_sql("04_ml_receita_diaria_concessionarias.sql"),
                "useLegacySql": False,
            }
        },
        location="US",
        project_id=PROJECT_ID,
    )

    train_ml_modelo_previsao = BigQueryInsertJobOperator(
        task_id="train_ml_modelo_previsao_faturamento",
        configuration={
            "query": {
                "query": read_sql("05_ml_modelo_previsao_faturamento.sql"),
                "useLegacySql": False,
            }
        },
        location="US",
        project_id=PROJECT_ID,
    )

    build_ml_previsao_faturamento = BigQueryInsertJobOperator(
        task_id="build_ml_previsao_faturamento_concessionarias",
        configuration={
            "query": {
                "query": read_sql("06_ml_previsao_faturamento_concessionarias.sql"),
                "useLegacySql": False,
            }
        },
        location="US",
        project_id=PROJECT_ID,
    )

    check_silver_has_rows = BigQueryCheckOperator(
        task_id="check_silver_vendas_has_rows",
        sql=f"SELECT COUNT(*) > 0 FROM `{PROJECT_ID}.{SILVER_DATASET}.vendas`",
        use_legacy_sql=False,
        location="US",
    )

    check_gold_concessionarias_has_rows = BigQueryCheckOperator(
        task_id="check_gold_faturamento_has_rows",
        sql=(
            f"SELECT COUNT(*) > 0 FROM "
            f"`{PROJECT_ID}.{GOLD_DATASET}.faturamento_por_concessionaria`"
        ),
        use_legacy_sql=False,
        location="US",
    )

    check_gold_vendedores_has_rows = BigQueryCheckOperator(
        task_id="check_gold_vendedores_has_rows",
        sql=f"SELECT COUNT(*) > 0 FROM `{PROJECT_ID}.{GOLD_DATASET}.performance_vendedores`",
        use_legacy_sql=False,
        location="US",
    )

    check_ml_previsao_has_rows = BigQueryCheckOperator(
        task_id="check_ml_previsao_faturamento_has_rows",
        sql=f"SELECT COUNT(*) > 0 FROM `{PROJECT_ID}.{GOLD_DATASET}.previsao_faturamento_concessionarias`",
        use_legacy_sql=False,
        location="US",
    )

    extract_postgres_to_gcs_bronze >> load_gcs_to_bigquery_bronze >> build_silver_vendas
    build_silver_vendas >> [build_gold_faturamento, build_gold_vendedores]
    build_silver_vendas >> build_ml_receita_diaria >> train_ml_modelo_previsao >> build_ml_previsao_faturamento
    build_gold_faturamento >> check_gold_concessionarias_has_rows
    build_gold_vendedores >> check_gold_vendedores_has_rows
    build_ml_previsao_faturamento >> check_ml_previsao_has_rows
    build_silver_vendas >> check_silver_has_rows
