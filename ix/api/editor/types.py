from typing import Optional, List, Literal
from uuid import UUID

from pydantic import BaseModel

from ix.api.chains.types import Position
from ix.api.components.types import NodeType as NodeTypePydantic
from ix.api.chains.types import Node as NodePydantic
from ix.api.chains.types import Edge as EdgePydantic
from ix.api.chains.types import Chain as ChainPydantic


class PositionUpdate(BaseModel):
    x: float
    y: float


class UpdatedRoot(BaseModel):
    root: Optional[UUID]
    old_roots: List[str]


class UpdateRoot(BaseModel):
    node_id: Optional[UUID]


class NewNodeEdge(BaseModel):
    """A new edge to be created with a node"""

    id: Optional[UUID] = None
    source_id: UUID | Literal["root"]
    target_id: UUID
    key: str


class AddNode(BaseModel):
    id: Optional[UUID]
    chain_id: Optional[UUID]
    class_path: str
    name: Optional[str]
    description: Optional[str]
    config: Optional[dict]
    position: Optional[Position]

    # optionally add edges to other nodes
    edges: Optional[List[NewNodeEdge]] = None


class UpdateNode(BaseModel):
    config: Optional[dict]
    name: Optional[str]
    description: Optional[str]
    position: Optional[Position]


class UpdateEdge(BaseModel):
    source_id: UUID
    target_id: UUID


class GraphModel(BaseModel):
    chain: ChainPydantic
    nodes: List[NodePydantic]
    edges: List[EdgePydantic]
    types: List[NodeTypePydantic]
