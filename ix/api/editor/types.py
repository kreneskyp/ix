from typing import Optional, List, Literal
from uuid import UUID

from pydantic import BaseModel, model_validator

from ix.api.chains.types import Position
from ix.api.components.types import NodeType as NodeTypePydantic
from ix.api.chains.types import Node as NodePydantic
from ix.api.chains.types import Edge as EdgePydantic
from ix.api.chains.types import Chain as ChainPydantic


class PositionUpdate(BaseModel):
    x: float
    y: float


class UpdatedRoot(BaseModel):
    roots: List[UUID]
    old_roots: List[UUID]


class UpdateRoot(BaseModel):
    node_ids: List[UUID]


class NewNodeEdge(BaseModel):
    """A new edge to be created with a node"""

    id: Optional[UUID] = None
    source_id: UUID | Literal["root"]
    target_id: UUID
    source_key: str
    target_key: str


class AddNode(BaseModel):
    id: Optional[UUID] = None
    chain_id: Optional[UUID] = None
    class_path: str
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[dict] = None
    position: Optional[Position] = None
    root: Optional[bool] = False

    # optionally add edges to other nodes
    edges: Optional[List[NewNodeEdge]] = None

    @model_validator(mode="before")
    def validate_root(cls, value) -> bool:
        # set root automatically for root nodes
        if value["class_path"] == "__ROOT__":
            value["root"] = True

        return value


class UpdateNode(BaseModel):
    config: Optional[dict]
    name: Optional[str]
    description: Optional[str]
    position: Optional[Position]


class UpdateEdge(BaseModel):
    source_id: UUID
    target_id: UUID
    target_key: str
    source_key: str


class GraphModel(BaseModel):
    chain: ChainPydantic
    nodes: List[NodePydantic]
    edges: List[EdgePydantic]
    types: List[NodeTypePydantic]


class GraphNodes(BaseModel):
    nodes: List[NodePydantic]
    types: List[NodeTypePydantic]
