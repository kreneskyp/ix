from functools import reduce
from typing import Any, Dict, Literal

OpenAPISchemaDict = Dict[str, Any]
HTTP_METHODS = Literal["get", "post", "put", "patch", "delete", "options", "head"]


def get_input_schema(
    schema: OpenAPISchemaDict, path: str, method: HTTP_METHODS
) -> Dict[str, Any]:
    """
    Extracts the JSON schema for the input of a specified HTTP method, converts it to a valid JSON schema,
    and uses references for nested objects named 'query', 'args', and 'body' (using the schema title if available).
    """

    def resolve_reference(schema, ref):
        parts = ref.split("/")
        return reduce(
            lambda sub_schema, key: sub_schema.get(key, {}), parts[1:], schema
        )

    def convert_to_json_schema(params, param_type, definitions, definition_name):
        properties = {}
        required = []

        for param in params:
            ref = param.get("$ref")
            param_schema = resolve_reference(schema, ref) if ref else param
            if param_schema.get("in") == param_type:
                name = param_schema["name"]
                param_properties = param_schema.get("schema", {})
                properties[name] = extract_nested_objects(
                    param_properties, definitions, definition_name
                )
                if param_schema.get("required", False):
                    required.append(name)

        return properties, required

    def extract_nested_objects(schema, definitions, definition_name):
        if isinstance(schema, dict):
            if (
                "type" in schema
                and schema["type"] == "object"
                and "properties" in schema
            ):
                definitions[definition_name] = schema
                return {"$ref": f"#/definitions/{definition_name}"}
            else:
                return {
                    k: extract_nested_objects(v, definitions, definition_name)
                    for k, v in schema.items()
                }
        elif isinstance(schema, list):
            return [
                extract_nested_objects(elem, definitions, definition_name)
                for elem in schema
            ]
        else:
            return schema

    result = {"type": "object", "properties": {}, "required": [], "definitions": {}}

    path_item = schema.get("paths", {}).get(path, {})
    method_item = path_item.get(method.lower(), {})

    path_properties, path_required = convert_to_json_schema(
        method_item.get("parameters", []), "path", result["definitions"], "Args"
    )
    query_properties, query_required = convert_to_json_schema(
        method_item.get("parameters", []), "query", result["definitions"], "Query"
    )

    if path_properties:
        result["properties"]["args"] = extract_nested_objects(
            {
                "type": "object",
                "properties": path_properties,
                "required": path_required,
            },
            result["definitions"],
            "Args",
        )

    if query_properties:
        result["properties"]["query"] = extract_nested_objects(
            {
                "type": "object",
                "properties": query_properties,
                "required": query_required,
            },
            result["definitions"],
            "Query",
        )

    if method.lower() in ["post", "put", "patch"]:
        request_body = method_item.get("requestBody", {})
        content = request_body.get("content", {})
        json_schema = content.get("application/json", {}).get("schema", {})
        ref = json_schema.get("$ref")
        body_schema = resolve_reference(schema, ref) if ref else json_schema
        if body_schema:
            body_definition_name = body_schema.get("title", "Body")
            result["properties"]["body"] = extract_nested_objects(
                body_schema, result["definitions"], body_definition_name
            )
            result["required"].append("body")

    if path_required:
        result["required"].append("path")
    if query_required:
        result["required"].append("query")

    return result


def get_action_schema(
    schema: OpenAPISchemaDict, path: str, method: HTTP_METHODS
) -> OpenAPISchemaDict:
    """Return subset of schema containing only the specified path and method."""
    schema = schema.copy()
    schema["paths"] = {path: {method: schema["paths"][path][method]}}
    return schema
