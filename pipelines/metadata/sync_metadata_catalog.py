from app.api.services.metadata_catalog_service import refresh_metadata_catalog


def main() -> None:
    result = refresh_metadata_catalog()
    print(
        "Persisted metadata catalog with "
        f"{result['dataset_count']} datasets at {result['generated_at']}.\n"
        f"Snapshot: {result['snapshot_path']}\n"
        f"Embeddings: {result['embedding_index_path']}"
    )


if __name__ == "__main__":
    main()
