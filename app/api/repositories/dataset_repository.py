from typing import Any, Dict, List, Optional

from app.api.services.mock_data import DATASETS


def list_datasets() -> List[Dict[str, Any]]:
    return DATASETS


def find_dataset_by_id(dataset_id: str) -> Optional[Dict[str, Any]]:
    for dataset in DATASETS:
        if dataset["dataset_id"] == dataset_id:
            return dataset
    return None
