import argparse
from datetime import datetime, timezone

from google.cloud import bigquery, storage


TABLES = [
    "cidades",
    "clientes",
    "concessionarias",
    "estados",
    "veiculos",
    "vendas",
    "vendedores",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def list_gcs_uris(bucket_name: str, table_name: str) -> list[str]:
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=f"novadrive/{table_name}/")
    uris = [f"gs://{bucket_name}/{blob.name}" for blob in blobs if blob.name.endswith(".jsonl")]
    return sorted(uris)


def load_table(project_id: str, dataset_id: str, bucket_name: str, table_name: str) -> None:
    client = bigquery.Client(project=project_id)

    uris = list_gcs_uris(bucket_name, table_name)
    if not uris:
        print(f"[{table_name}] no .jsonl files found in GCS")
        return

    table_id = f"{project_id}.{dataset_id}.{table_name}_raw"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
    )

    load_job = client.load_table_from_uri(uris, table_id, job_config=job_config)
    load_job.result()

    table = client.get_table(table_id)
    print(f"[{table_name}] files={len(uris)} loaded rows={table.num_rows} into {table_id}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--bucket", required=True)
    args = parser.parse_args()

    print(f"starting bronze load at {utc_now().isoformat()}")

    for table in TABLES:
        load_table(args.project, args.dataset, args.bucket, table)


if __name__ == "__main__":
    main()
