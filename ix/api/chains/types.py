from datetime import datetime
from typing import (
    List,
    Optional,
    Literal,
)
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, root_validator

from ix.utils.graphene.pagination import QueryPage


class Chain(BaseModel):
    id: Optional[UUID]
    name: str
    description: str
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class CreateChain(BaseModel):
    name: str
    description: Optional[str]


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
        orm_mode = True


class Edge(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    source_id: UUID
    target_id: UUID
    key: Optional[str]
    chain_id: UUID
    relation: Literal["LINK", "PROP"]
    input_map: Optional[dict]

    class Config:
        orm_mode = True

    @root_validator
    def validate_edge(cls, values):
        if values.get("relation") == "PROP" and not values.get("key"):
            raise ValueError("'key' is required for 'PROP' relation type.")

        return values
