from typing import List, Optional

from pydantic import BaseModel, Field


class DatasetItem(BaseModel):
    dataset_id: str
    name: str
    description: Optional[str] = None
    owner: Optional[str] = None
    type: str


class DatasetListResponse(BaseModel):
    items: List[DatasetItem]
    total: int
    filters: dict


class DatasetColumn(BaseModel):
    name: str
    data_type: Optional[str] = None
    nullable: Optional[bool] = None
    description: Optional[str] = None


class DatasetDocument(BaseModel):
    document_id: str
    title: str


class DatasetDetailResponse(BaseModel):
    dataset_id: str
    name: str
    catalog: Optional[str] = None
    schema_name: Optional[str] = Field(default=None, alias="schema")
    table: Optional[str] = None
    type: str
    description: Optional[str] = None
    owner: Optional[str] = None
    columns: List[DatasetColumn]
    documentation: List[DatasetDocument]

    model_config = {
        "populate_by_name": True,
    }
