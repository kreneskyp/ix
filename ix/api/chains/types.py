import inspect
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    Dict,
    List,
    Any,
    Optional,
    Type,
    Literal,
    get_args,
    get_origin,
    Union,
    Callable,
)
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, model_validator
from pydantic_core import PydanticUndefined

from ix.utils.graphene.pagination import QueryPage
from ix.utils.pydantic import get_model_fields


class InputType(str, Enum):
    INPUT = "input"
    SLIDER = "slider"
    SECRET = "secret"
    TEXTAREA = "textarea"
    SELECT = "select"


class Choice(BaseModel):
    label: str
    value: Any


def cap_first(s: str) -> str:
    """Capitalizes the first character of the input string."""
    return s[0].upper() + s[1:] if s else ""


def is_optional(type_hint) -> bool:
    """detect if type_hint is Optional[T]"""
    return get_origin(type_hint) is Union and type(None) in get_args(type_hint)


class Chain(BaseModel):
    id: Optional[UUID]
    name: str
    description: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class CreateChain(BaseModel):
    name: str
    description: Optional[str]


class ChainQueryPage(QueryPage[Chain]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[Chain]


class Position(BaseModel):
    x: float
    y: float


@dataclass
class ParsedField:
    """Field parsed from a pydantic model or a method signature."""

    name: str
    type_: Any
    default: Any = None
    required: bool = False
    choices: List[Dict[str, str]] = None


def parse_enum_choices(enum_cls: Enum) -> List[Dict[str, str]]:
    return [
        {"label": name, "value": value.value}
        for name, value in enum_cls.__members__.items()
    ]


class NodeTypeField(BaseModel):
    """
    Represents a field in a component that can be configured. This includes both
    typing information and UX information.

    This class includes `get_fields_from_model` and `get_fields_from_method` helpers
     for auto-importing fields from Pydantic model and python methods respectively.

    Args:
        name (str): The name of the field. Used to set and retrieve the value on the object.
        label (str): The label for the field. Displayed in the user interface (UX).
        type (str): The type of the field. Used for validation and formatting.
        default (Any): The default value for the field when creating a new object.
        required (bool, optional): Indicates if the field is required. Defaults to True.
        input_type (InputType, optional): Selects the UX component for the field. Defaults to InputType.TEXT.
        min (float, optional): The minimum value for the field (required for InputType.SLIDER). Defaults to None.
        max (float, optional): The maximum value for the field (required for InputType.SLIDER). Defaults to None.
        choices (List[Choice], optional): The choices for the field (required for InputType.SELECT). Defaults to None.
        step (float, optional): The step value for the field (required for InputType.SLIDER). Defaults to None.
        style (Dict[str, Any], optional): The Chakra UI style properties applied to the UX component. Defaults to None.
    """

    name: str
    label: Optional[str] = None
    type: str
    default: Optional[Any] = None
    required: bool = True
    input_type: Optional[InputType] = None
    min: Optional[float] = None
    max: Optional[float] = None
    choices: Optional[List[Choice]] = None
    step: Optional[float] = None
    style: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    def validate_min_max(cls, values):
        input_type = values.get("input_type")
        min_value = values.get("min")
        max_value = values.get("max")
        choices = values.get("choices")
        step = values.get("step")

        if input_type == InputType.SLIDER and (min_value is None or max_value is None):
            raise ValueError("'min' and 'max' are required for 'SLIDER' input type.")

        if input_type == InputType.SELECT and choices is None:
            raise ValueError("'choices' are required for 'SELECT' input type.")

        if input_type == InputType.SLIDER and step is None:
            raise ValueError("'step' is required for 'SLIDER' input type.")

        return values

    @classmethod
    def get_fields_from_model(
        cls,
        model: Type[BaseModel] | Type[ABC],
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        field_options: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        field_objs = []

        annotations = {}
        if hasattr(model, "__annotations__"):
            annotations.update(model.__annotations__)
        if issubclass(model, ABC):
            for base in model.__bases__:
                if hasattr(base, "__annotations__"):
                    annotations.update(base.__annotations__)

        for field_name, field_type in annotations.items():
            if include and field_name not in include:
                continue
            if exclude and field_name in exclude:
                continue

            # skip fields that aren't primitive types. objects are handled separately
            # as connectors.
            if isinstance(field_type, type) and issubclass(
                field_type, (BaseModel, ABC)
            ):
                continue

            default = None
            if issubclass(model, BaseModel):
                # Pydantic v2 compat: __fields__ renamed to model_fields
                model_fields = get_model_fields(model)
                model_field = model_fields.get(field_name)
                if model_field:
                    default = model_field.default
                    if default is PydanticUndefined:
                        default = None
            elif issubclass(model, ABC):
                default = model.__dict__.get(field_name, None)
            required = default is None and not is_optional(field_type)

            field_objs.append(
                ParsedField(
                    name=field_name,
                    type_=field_type,
                    default=default,
                    required=required,
                )
            )

        return cls._get_fields(field_objs, field_options)

    @classmethod
    def get_fields_from_method(
        cls,
        method: Callable,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        field_options: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        fields = []
        signature = inspect.signature(method)

        # TODO: does not support @staticmethod, which drops first argument
        #       when using inspect.signature.

        for param_name, param in signature.parameters.items():
            if include and param_name not in include:
                continue
            if exclude and param_name in exclude:
                continue

            if param.default is inspect._empty:
                is_required = True
                default = None
            else:
                is_required = False
                default = param.default
            fields.append(
                ParsedField(
                    name=param_name,
                    type_=param.annotation,
                    default=default,
                    required=is_required,
                )
            )

        return cls._get_fields(fields, field_options)

    @staticmethod
    def _get_fields(
        fields: List[ParsedField],
        field_options: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        results = []

        for field in fields:
            origin = get_origin(field.type_)
            is_literal = origin is Literal
            _is_optional = is_optional(field.type_)

            root_field = field.type_
            if is_literal:
                root_field = str
            elif _is_optional:
                root_field = get_args(field.type_)[0]

            if root_field is bool:
                # Backwards compatibility for "boolean" type
                # TODO: cleanup poor naming choice
                field_type_name = "boolean"
            else:
                field_type_name = getattr(root_field, "__name__", str(root_field))

            field_info = {
                "name": field.name,
                "label": cap_first(field.name),
                "type": field_type_name,
                "default": field.default,
                "required": field.required,
            }

            if is_literal:
                field_info["choices"] = [
                    {"label": cap_first(arg), "value": arg}
                    for arg in get_args(field.type_)
                ]
            elif isinstance(root_field, type) and issubclass(root_field, Enum):
                field_info["type"] = "str"
                field_info["choices"] = parse_enum_choices(root_field)

            if field_info.get("choices", None):
                field_info["input_type"] = "select"

            if field_options and field.name in field_options:
                field_info.update(field_options[field.name])

            results.append(field_info)

        return results

    @classmethod
    def get_fields(
        cls,
        obj: Callable | Type[BaseModel] | Type[ABC],
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        field_options: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        if isinstance(obj, type) and issubclass(obj, BaseModel | ABC):
            return cls.get_fields_from_model(
                obj, include=include, exclude=exclude, field_options=field_options
            )
        elif isinstance(obj, Callable):
            return cls.get_fields_from_method(
                obj, include=include, exclude=exclude, field_options=field_options
            )

        raise ValueError(f"Invalid object type: {type(obj)}")


NodeTypes = Literal[
    "agent",
    "chain",
    "chain_list",
    "document_loader",
    "embeddings",
    "index",
    "llm",
    "memory",
    "memory_backend",
    "output_parser",
    "parser",
    "prompt",
    "retriever",
    "tool",
    "toolkit",
    "text_splitter",
    "vectorstore",
]


class Connector(BaseModel):
    """
    A connection point for a property on a node.
    """

    key: str
    type: Literal["source", "target"]

    # Simplified categorization of LangChain components. Class inheritance
    # can't be checked in JS so these categories are used for a proxy instead.
    source_type: NodeTypes | List[NodeTypes]

    # The object type this should be converted to. Used when the source will
    # be converted to another type. e.g. VectorStore.as_retriever()
    as_type: Optional[NodeTypes] = None

    # Allow more than one connection to this connector
    multiple: bool = False

    # Chains connected to this property will join into an implicit SequentialChain
    # when auto_sequence is True. Disable for chains to be stored as a list.
    auto_sequence: bool = False


class NodeType(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    class_path: str = Field(..., max_length=255)
    type: str = Field(..., max_length=255)
    display_type: str = Field(default="node", max_length=10)
    connectors: Optional[List[Connector]] = None
    fields: Optional[List[NodeTypeField]] = None
    child_field: Optional[str] = Field(None, max_length=32)

    class Config:
        from_attributes = True

    @staticmethod
    def generate_config_schema(fields: List[NodeTypeField]) -> dict:
        """Generates a JSON schema from a list of NodeTypeField objects."""
        schema = {"type": "object", "properties": {}, "required": []}
        for field in fields:
            # Determine the type of the field for the JSON schema
            if field.type in {"str", "string"}:
                schema_type = "string"
            elif field.type in {"number", "float", "int", "integer"}:
                schema_type = "number"
            elif field.type in {"bool", "boolean"}:
                schema_type = "boolean"
            else:
                schema_type = "object"

            schema["properties"][field.name] = {
                "type": schema_type,
                "default": field.default,
            }
            if field.required:
                schema["required"].append(field.name)

            if field.input_type == InputType.SLIDER:
                schema["properties"][field.name]["minimum"] = field.min
                schema["properties"][field.name]["maximum"] = field.max
                schema["properties"][field.name]["multipleOf"] = field.step

            elif field.input_type == InputType.SELECT:
                schema["properties"][field.name]["enum"] = [
                    choice.value for choice in field.choices
                ]

        return schema


class NodeTypePage(QueryPage[NodeType]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[NodeType]


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


class PositionUpdate(BaseModel):
    x: float
    y: float
