from app.api.schemas.lineage import LineageResponse
from app.api.services.mock_data import LINEAGE


def get_lineage(dataset_id: str) -> LineageResponse:
    lineage = LINEAGE.get(dataset_id)

    if lineage:
        return LineageResponse(
            dataset_id=lineage["dataset_id"],
            upstream=lineage["upstream"],
            downstream=lineage["downstream"],
            related_jobs=lineage["related_jobs"],
        )

    return LineageResponse(
        dataset_id=dataset_id,
        upstream=[],
        downstream=[],
        related_jobs=[],
    )
