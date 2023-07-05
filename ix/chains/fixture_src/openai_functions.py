from ix.chains.fixture_src.common import VERBOSE
from ix.chains.fixture_src.targets import LLM_TARGET, MEMORY_TARGET, PROMPT_TARGET

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

OPENAPI_CHAIN = {
    "class_path": "langchain.chains.openai_functions.openapi.get_openapi_chain",
    "type": "chain",
    "name": "OpenAPI with OpenAI Functions",
    "description": "Chain that uses OpenAI Functions to call OpenAPI endpoints.",
    "connectors": [LLM_TARGET, MEMORY_TARGET, PROMPT_TARGET],
    "fields": [
        VERBOSE,
        {
            "name": "spec",
            "type": "string",
            "label": "OpenAPI URL",
            "style": {
                "width": "500px",
            },
        },
    ],
}
