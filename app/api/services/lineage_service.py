from app.api.repositories.lineage_repository import find_lineage_by_dataset_id
from app.api.schemas.lineage import LineageResponse


def get_lineage(dataset_id: str) -> LineageResponse:
    lineage = find_lineage_by_dataset_id(dataset_id)

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
