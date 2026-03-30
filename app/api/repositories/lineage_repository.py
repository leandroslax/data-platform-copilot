from typing import Any, Dict, Optional

from app.api.services.mock_data import LINEAGE


def find_lineage_by_dataset_id(dataset_id: str) -> Optional[Dict[str, Any]]:
    return LINEAGE.get(dataset_id)
