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


JSON_DATA_CLASS_PATH = "ix.chains.components.json.JSONData"
JSON_DATA = {
    "class_path": JSON_DATA_CLASS_PATH,
    "name": "JSON Data",
    "description": "Parse a value from inputs using a JSONPath",
    "type": "data",
    "fields": [
        {
            "name": "data",
            "description": "JSON data",
            "type": "list",
            "input_type": "textarea",
            "required": True,
            "style": {
                "width": "100%",
            },
        }
    ],
}

JSON = [JSON_PATH, JSON_DATA]
