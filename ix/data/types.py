from pydantic import BaseModel, UUID4, Field, model_validator
from typing import Dict, Optional, List, Literal, Any
from ix.utils.graphene.pagination import QueryPage


class SchemaBase(BaseModel):
    type: Literal["json", "openapi"]
    name: str = Field(max_length=128)
    description: str
    value: Dict[str, Any] = Field(default_factory=dict, description="schema as a dict")
    meta: Dict[str, Any] = Field(
        default_factory=dict, description="schema metadata as a dict"
    )


class EditSchema(SchemaBase):
    """New schema definition"""

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    def default_meta(cls, values):
        if not values.get("meta", None):
            values["meta"] = {}
        return values


class Schema(SchemaBase):
    """JSON and OpenAPI schemas"""

    id: UUID4 = Field(
        default=None, description="ID. Do not set when creating or updating"
    )

    class Config:
        from_attributes = True


class SchemaPage(QueryPage[Schema]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[Schema]


class Data(BaseModel):
    """Data object matching a schema definition"""

    id: Optional[UUID4] = None
    name: str = Field(max_length=128)
    description: str
    schema_id: Optional[UUID4] = None
    value: Dict[str, Any] = Field(default_factory=dict, description="value as a dict")
    meta: Dict[str, Any] = Field(default_factory=dict, description="metadata as a dict")

    class Config:
        from_attributes = True


class DataPage(QueryPage[Data]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[Data]
