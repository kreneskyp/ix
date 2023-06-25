FUNCTION_SCHEMA = {
    "class_path": "ix.chains.functions.FunctionSchema",
    "type": "tool",
    "name": "Function Schema",
    "description": "Describes a function using json. Compatible with OpenAI",
    "fields": [
        {
            "name": "name",
            "type": "string",
            "default": "",
        },
        {
            "name": "description",
            "type": "string",
            "default": "",
        },
        {
            "name": "parameters",
            "type": "json",
            "default": "",
        },
    ],
}

FUNCTION_OUTPUT_PARSER = {
    "class_path": "ix.chains.functions.OpenAIFunctionParser",
    "type": "output_parser",
    "name": "Function Output Parser",
    "description": "Parses the output of a function",
    "fields": [
        {
            "name": "parse_json",
            "type": "boolean",
            "default": False,
        }
    ],
}

FUNCTION_CALL = {
    "name": "function_call",
    "type": "string",
}
