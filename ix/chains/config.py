from enum import Enum
from typing import Dict, List, Any, Optional, Type, Literal, get_args, get_origin, Union

from pydantic import BaseModel, Field, root_validator


class InputType(str, Enum):
    SLIDER = "slider"
    SECRET = "secret"
    TEXT = "text"
    SELECT = "select"


class Choice(BaseModel):
    label: str
    value: Any


def cap_first(s: str) -> str:
    """Capitalizes the first character of the input string."""
    return s[0].upper() + s[1:] if s else ""


def is_optional(type_hint):
    return get_origin(type_hint) is Union and type(None) in get_args(type_hint)


class NodeTypeField(BaseModel):
    """
    Represents a field in a component that can be configured. This includes both
    typing information and UX information.

    This class includes `get_fields` helper for auto-importing fields from a Pydantic model.

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
    label: str
    type: str
    default: Any
    required: bool = True
    input_type: InputType = InputType.TEXT
    min: Optional[float] = None
    max: Optional[float] = None
    choices: Optional[List[Choice]] = None
    step: Optional[float] = None
    style: Optional[Dict[str, Any]] = None

    @root_validator
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

    @staticmethod
    def get_fields(
        model: Type[BaseModel],
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        field_options: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        fields = []
        exclude = exclude or []
        include = include or []

        for field_name, field in model.__annotations__.items():
            origin = get_origin(field)
            is_literal = origin is Literal
            _is_optional = is_optional(field)

            root_field = field
            if is_literal:
                root_field = str
            elif _is_optional:
                root_field = get_args(field)[0]

            if root_field is bool:
                # Backwards compatibility for "boolean" type
                # TODO: cleanup poor naming choice
                field_type_name = "boolean"
            else:
                field_type_name = getattr(root_field, "__name__", str(root_field))

            if field_name in exclude:
                continue
            if include and field_name not in include:
                continue
            if isinstance(field, type) and issubclass(field, BaseModel):
                continue

            model_field = model.__fields__.get(field_name)
            field_info = {
                "name": field_name,
                "label": cap_first(field_name),
                "type": field_type_name,
                "default": model_field.default,
                "required": model_field.required,
            }

            if is_literal:
                field_info["choices"] = [
                    {"label": cap_first(arg), "value": arg} for arg in get_args(field)
                ]

            if field_options and field_name in field_options:
                field_info.update(field_options[field_name])

            fields.append(field_info)

        return fields


class Connector(BaseModel):
    """
    A connection point for a property on a node.
    """

    key: str
    type: Literal["source", "target"]

    # Simplified categorization of LangChain components. Class inheritance
    # can't be checked in JS so these categories are used for a proxy instead.
    source_types: Literal[
        "agent",
        "chain",
        "chain_list",
        "document_loader",
        "embeddings",
        "index",
        "llm",
        "memory",
        "memory_backend",
        "prompt",
        "retriever",
        "tool",
        "toolkit",
        "text_splitter",
    ]

    # Allow more than one connection to this connector
    multiple: bool = False

    # Chains connected to this property will join into an implicit SequentialChain
    # when auto_sequence is True. Disable for chains to be stored as a list.
    auto_sequence: bool = False


class NodeType(BaseModel):
    """
    Pydantic equivalent of ix.chains.model.NodeType. Used to validate fixtures.
    """

    class_path: str = Field(..., description="The class path of the tool.")
    type: str = Field(..., description="The type of the tool.")
    name: str = Field(..., description="The name of the tool.")
    description: str = Field(..., description="The description of the tool.")
    fields: List[NodeTypeField] = Field(default_factory=list)
    connectors: List[Connector] = Field(default_factory=list)
    child_field: Optional[str]
