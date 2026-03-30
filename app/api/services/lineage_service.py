from app.api.schemas.lineage import LineageResponse


def get_lineage(dataset_id: str) -> LineageResponse:
    return LineageResponse(
        dataset_id=dataset_id,
        upstream=[],
        downstream=[],
        related_jobs=[],
    )
