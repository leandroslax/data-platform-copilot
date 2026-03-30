from typing import List

from pydantic import BaseModel


class LineageResponse(BaseModel):
    dataset_id: str
    upstream: List[str]
    downstream: List[str]
    related_jobs: List[str]
