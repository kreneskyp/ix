from typing import Any, Dict, List, Optional, Type
from typing_extensions import TypedDict, Annotated
import operator


# Mapping of operators available to annotate fields with
# i.e. Annotated[str, operator.add]. LangGraph state machine
# applies the operator to the field value on state updates.
operator_mapping = {
    "add": operator.add,
}


def resolve_reference(ref: str, definitions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve a $ref to the actual schema it refers to within definitions.
    """
    ref_path = ref.split("/")
    ref_name = ref_path[-1]
    return definitions.get(ref_name, {})


def combine_schemas(
    allOf: List[Dict[str, Any]], definitions: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Combine schemas specified in allOf by merging their properties.
    """
    combined_schema = {"properties": {}, "required": [], "type": "object"}
    for schema in allOf:
        if "$ref" in schema:
            ref_schema = resolve_reference(schema["$ref"], definitions)
            schema = ref_schema
        combined_schema["properties"].update(schema.get("properties", {}))
        combined_schema["required"].extend(schema.get("required", []))
    return combined_schema


def convert_type(prop: Dict[str, Any], definitions: Dict[str, Any]) -> Any:
    """
    Convert a JSON schema property to a Python type, handling references,
    allOf, anyOf, and custom annotations for operations.
    """
    if "$ref" in prop:
        ref_schema = resolve_reference(prop["$ref"], definitions)
        return convert_type(ref_schema, definitions)

    if "allOf" in prop:
        combined_schema = combine_schemas(prop["allOf"], definitions)
        return jsonschema_to_typeddict(combined_schema, definitions)

    # Simplified type conversion for demonstration
    type_mapping = {
        "string": str,
        "number": float,
        "integer": int,
        "boolean": bool,
        "array": List[Any],  # Note: Items not handled in this example
        "object": Dict[str, Any],
    }

    prop_type = type_mapping.get(prop.get("type"), Any)

    # Handle custom operation annotations within the field definition
    if "operation" in prop:
        operation = operator_mapping.get(prop["operation"])
        if operation:
            return Annotated[prop_type, operation]

    return prop_type


def jsonschema_to_typeddict(
    schema: Dict[str, Any], definitions: Optional[Dict[str, Any]] = None
) -> Type[TypedDict]:
    if definitions is None:
        definitions = schema.get("definitions", {})

    title = schema.get("title", "DynamicTypedDict")
    properties = schema.get("properties", {})

    annotations = {}
    for name, prop in properties.items():
        python_type = convert_type(prop, definitions)
        annotations[name] = python_type

    # Dynamically create TypedDict
    TypedDictClass = TypedDict(title, annotations)

    return TypedDictClass
