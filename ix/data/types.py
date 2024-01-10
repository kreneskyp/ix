from pydantic import BaseModel, UUID4, Field
from typing import Dict, Optional, List
from ix.utils.graphene.pagination import QueryPage


class Schema(BaseModel):
    id: Optional[UUID4] = None
    type: str
    name: str = Field(max_length=128)
    description: str
    value: Dict = Field(default_factory=dict)
    meta: Dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


class SchemaPage(QueryPage[Schema]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[Schema]


class Data(BaseModel):
    id: Optional[UUID4] = None
    name: str = Field(max_length=128)
    description: str
    schema_id: Optional[UUID4] = None
    value: Dict = Field(default_factory=dict)
    meta: Dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


class DataPage(QueryPage[Data]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[Data]
