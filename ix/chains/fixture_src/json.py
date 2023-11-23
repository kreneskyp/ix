from ix.api.components.types import NodeTypeField
from ix.chains.components.json import JSONPath

JSON_PATH_CLASS_PATH = "ix.chains.components.json.JSONPath"
JSON_PATH = {
    "class_path": JSON_PATH_CLASS_PATH,
    "name": "JSON Path",
    "description": "Parse a value from inputs using a JSONPath",
    "type": "chain",
    "fields": NodeTypeField.get_fields(
        JSONPath,
        include=["path", "return_list"],
    ),
}

JSON = [JSON_PATH]
