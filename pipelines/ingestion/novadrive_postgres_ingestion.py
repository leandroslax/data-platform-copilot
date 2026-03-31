import argparse
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List

import psycopg2
from google.cloud import storage
from psycopg2.extras import RealDictCursor


TABLES = [
    "cidades",
    "clientes",
    "concessionarias",
    "estados",
    "veiculos",
    "vendas",
    "vendedores",
]

CHECKPOINT_PATH = Path("pipelines/ingestion/state/novadrive_checkpoints.json")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def load_checkpoints() -> Dict[str, str]:
    if not CHECKPOINT_PATH.exists():
        return {}
    return json.loads(CHECKPOINT_PATH.read_text())


def save_checkpoints(checkpoints: Dict[str, str]) -> None:
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_PATH.write_text(json.dumps(checkpoints, indent=2, sort_keys=True))


def get_connection():
    return psycopg2.connect(
        host=os.environ["NOVADRIVE_DB_HOST"],
        port=os.environ.get("NOVADRIVE_DB_PORT", "5432"),
        dbname=os.environ["NOVADRIVE_DB_NAME"],
        user=os.environ["NOVADRIVE_DB_USER"],
        password=os.environ["NOVADRIVE_DB_PASSWORD"],
        cursor_factory=RealDictCursor,
    )


def fetch_rows(conn, table: str, mode: str, checkpoint: str | None) -> List[Dict[str, Any]]:
    with conn.cursor() as cur:
        if mode == "incremental" and checkpoint:
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
        return [dict(row) for row in cur.fetchall()]


def serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def normalize_rows(rows: List[Dict[str, Any]], table: str, extracted_at: str) -> List[Dict[str, Any]]:
    normalized = []
    for row in rows:
        item = {key: serialize_value(value) for key, value in row.items()}
        item["source_system"] = "novadrive_postgres"
        item["source_table"] = table
        item["ingested_at"] = extracted_at
        normalized.append(item)
    return normalized


def to_ndjson(rows: List[Dict[str, Any]]) -> str:
    return "\n".join(json.dumps(row, ensure_ascii=True) for row in rows)


def upload_to_gcs(bucket_name: str, table: str, rows: List[Dict[str, Any]], extracted_at: datetime) -> str:
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    date_part = extracted_at.strftime("%Y-%m-%d")
    hour_part = extracted_at.strftime("%H")
    object_name = (
        f"novadrive/{table}/extract_date={date_part}/extract_hour={hour_part}/"
        f"part-{extracted_at.strftime('%Y%m%dT%H%M%S')}.jsonl"
    )

    blob = bucket.blob(object_name)
    blob.upload_from_string(
        to_ndjson(rows),
        content_type="application/x-ndjson",
    )
    return f"gs://{bucket_name}/{object_name}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["full", "incremental"], required=True)
    parser.add_argument("--bucket", required=True)
    args = parser.parse_args()

    checkpoints = load_checkpoints()
    extracted_at = utc_now()
    extracted_at_iso = extracted_at.isoformat()

    conn = get_connection()
    updated_checkpoints = dict(checkpoints)

    try:
        for table in TABLES:
            checkpoint = checkpoints.get(table)
            rows = fetch_rows(conn, table, args.mode, checkpoint)

            if not rows:
                print(f"[{table}] no rows returned")
                continue

            normalized_rows = normalize_rows(rows, table, extracted_at_iso)
            gcs_uri = upload_to_gcs(args.bucket, table, normalized_rows, extracted_at)
            updated_checkpoints[table] = extracted_at_iso

            print(f"[{table}] rows={len(normalized_rows)} uploaded={gcs_uri}")
    finally:
        conn.close()

    save_checkpoints(updated_checkpoints)
    print(f"checkpoints saved to {CHECKPOINT_PATH}")


if __name__ == "__main__":
    main()
