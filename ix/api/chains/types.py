from datetime import datetime
from typing import (
    List,
    Optional,
    Literal,
)
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, model_validator
from pydantic_core import PydanticUndefined

from ix.utils.graphene.pagination import QueryPage
from ix.utils.pydantic import get_model_fields


class Chain(BaseModel):
    id: Optional[UUID]
    name: str
    description: str
    created_at: Optional[datetime]
    is_agent: bool = True

    # agent pass through properties
    alias: Optional[str]

    class Config:
        from_attributes = True


class CreateChain(BaseModel):
    name: str
    description: Optional[str]
    is_agent: bool = True

    # agent pass through properties
    alias: Optional[str]

    @root_validator
    def validate_chain(cls, values):
        if values.get("is_agent") and not values.get("alias"):
            values["alias"] = "unnamed"
        return values


class UpdateChain(CreateChain):
    pass


class ChainQueryPage(QueryPage[Chain]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[Chain]


class Position(BaseModel):
    x: float
    y: float


class Node(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    chain_id: UUID
    class_path: str = Field(..., title="The path to the class")
    node_type_id: Optional[UUID]
    root: bool = False

    config: dict = Field(default_factory=dict)
    name: Optional[str]
    description: Optional[str]
    position: Position = {"x": 0, "y": 0}

    class Config:
        from_attributes = True


class Edge(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    source_id: UUID
    target_id: UUID
    key: Optional[str]
    chain_id: UUID
    relation: Literal["LINK", "PROP"]
    input_map: Optional[dict] = None

    class Config:
        from_attributes = True

    @model_validator(mode="after")
    def validate_edge(cls, instance: "Edge") -> "Edge":
        if instance.relation == "PROP" and not instance.key:
            raise ValueError("'key' is required for 'PROP' relation type.")

        return instance
