from typing import List, Optional

from pydantic import BaseModel


class SearchResult(BaseModel):
    dataset_id: str
    name: str
    owner: Optional[str] = None
    description: Optional[str] = None
    score: float
    source_system: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    items: List[SearchResult]
    total: int


class MetadataSyncResponse(BaseModel):
    dataset_count: int
    generated_at: str
    snapshot_path: str
    embedding_index_path: str
