from datetime import datetime
from typing import Optional, List, Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Chain(BaseModel):
    id: Optional[UUID]
    name: str
    description: str
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class Position(BaseModel):
    x: float
    y: float


class NodeType(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    class_path: str = Field(..., max_length=255)
    type: str = Field(..., max_length=255)
    display_type: str = Field(..., max_length=10)
    connectors: Optional[List[dict]] = None
    fields: Optional[List[dict]] = None
    child_field: Optional[str] = Field(None, max_length=32)

    class Config:
        orm_mode = True


class Node(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    chain_id: UUID
    class_path: str = Field(..., title="The path to the class")
    node_type_id: Optional[UUID]

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
    key: str
    chain_id: UUID
    relation: Literal["LINK", "PROP"]
    input_map: Optional[dict]

    class Config:
        orm_mode = True
