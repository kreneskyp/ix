from ix.api.chains.types import NodeTypeField
from ix.chains.fixture_src.common import VERBOSE
from ix.chains.fixture_src.targets import LLM_TARGET, MEMORY_TARGET, PROMPT_TARGET, OUTPUT_PARSER_TARGET
from ix.chains.data import GenerateSchema

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
    "class_path": "ix.chains.openapi.get_openapi_chain_async",
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

GENERATE_SCHEMA = {
    "class_path": "ix.chains.data.GenerateSchema",
    "type": "chain",
    "name": "Generate Schema",
    "description": "Generate a data object using an OpenAI function to format it",
    "connectors": [LLM_TARGET, MEMORY_TARGET, PROMPT_TARGET, OUTPUT_PARSER_TARGET],
    "fields": [VERBOSE] + NodeTypeField.get_fields(
        GenerateSchema,
        include=[
            "input_key",
            "output_key",
        ],
    )
}

OPEN_AI_FUNCTIONS_CHAINS = [
    FUNCTION_SCHEMA,
    FUNCTION_OUTPUT_PARSER,
    OPENAPI_CHAIN,
    GENERATE_SCHEMA,
]
