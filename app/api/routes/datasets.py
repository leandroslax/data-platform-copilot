from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/datasets")
def list_datasets(
    q: str | None = Query(default=None),
    catalog: str | None = Query(default=None),
    schema: str | None = Query(default=None),
    owner: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
) -> dict:
    return {
        "items": [],
        "total": 0,
        "filters": {
            "q": q,
            "catalog": catalog,
            "schema": schema,
            "owner": owner,
            "limit": limit,
        },
    }


@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: str) -> dict:
    return {
        "dataset_id": dataset_id,
        "name": dataset_id,
        "catalog": None,
        "schema": None,
        "table": None,
        "type": "table",
        "description": None,
        "owner": None,
        "columns": [],
        "documentation": [],
    }
