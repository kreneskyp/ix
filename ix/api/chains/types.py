from datetime import datetime
from typing import (
    List,
    Optional,
    Literal,
)
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, model_validator

from ix.utils.graphene.pagination import QueryPage


class Chain(BaseModel):
    id: Optional[UUID]
    name: str
    description: str
    created_at: Optional[datetime]
    is_agent: bool = True

    # agent pass through properties
    alias: Optional[str] = None

    class Config:
        from_attributes = True


class CreateChain(BaseModel):
    name: str
    description: Optional[str]
    is_agent: bool = True

    # agent pass through properties
    alias: Optional[str] = None

    @model_validator(mode="before")
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

    def get_input_keys(self, node_type: NodeType) -> List[str]:
        """Input keys for this node. Includes both the static "in" and subfields."""
        keys = ["in"]
        if in_connector := node_type.connector_map.get("in"):
            if in_connector.from_field:
                field_value = self.config.get(in_connector.from_field)
                if field_value:
                    keys.extend(field_value)
            elif in_connector.fields:
                keys.extend(in_connector.fields)
        return keys

    def get_output_keys(self, node_type: NodeType) -> List[str]:
        """Output keys for this node. Includes both the static "out" and subfields."""
        keys = ["out"]
        if out_connector := node_type.connector_map.get("out"):
            if out_connector.from_field:
                field_value = self.config.get(out_connector.from_field)
                keys.extend(field_value)
            elif out_connector.fields:
                keys.extend(out_connector.fields)
        return keys

    def get_config_keys(self, node_type: NodeType) -> List[str]:
        keys = []
        for key, connector in node_type.connector_map.items():
            if connector.init_type == "config":
                keys.append(key)
        return keys

    def get_bind_keys(self, node_type: NodeType) -> List[str]:
        keys = []
        for key, connector in node_type.connector_map.items():
            if connector.init_type == "bind":
                keys.append(key)
        return keys


class Edge(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    source_id: UUID
    target_id: UUID
    source_key: Optional[str] = None
    target_key: Optional[str] = None
    chain_id: UUID
    relation: Literal["LINK", "PROP"]
    input_map: Optional[dict] = None

    class Config:
        from_attributes = True

    @model_validator(mode="after")
    def validate_edge(cls, instance: "Edge") -> "Edge":
        if instance.relation == "PROP" and not instance.target_key:
            raise ValueError("'target_key' is required for 'PROP' relation type.")

        return instance
