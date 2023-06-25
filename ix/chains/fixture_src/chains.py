from ix.chains.fixture_src.common import VERBOSE
from ix.chains.fixture_src.openai_functions import FUNCTION_CALL
from ix.chains.fixture_src.targets import (
    PROMPT_TARGET,
    MEMORY_TARGET,
    LLM_TARGET,
    FUNCTION_TARGET,
    OUTPUT_PARSER_TARGET,
)

LLM_CHAIN = {
    "class_path": "ix.chains.llm_chain.LLMChain",
    "type": "chain",
    "name": "LLM Chain",
    "description": "Chain that prompts an LLM for a completion.",
    "connectors": [
        LLM_TARGET,
        MEMORY_TARGET,
        PROMPT_TARGET,
        FUNCTION_TARGET,
        OUTPUT_PARSER_TARGET,
    ],
    "fields": [
        VERBOSE,
        FUNCTION_CALL,
        {
            "name": "output_key",
            "type": "string",
            "default": "text",
        },
    ],
}

LLM_TOOL_CHAIN = dict(
    class_path="ix.chains.tool_chain.LLMToolChain",
    type="chain",
    name="LLM Tool Chain",
    description="Chain that prompts an LLM for a completion. It has a set of tools available to the prompt",
    connectors=[LLM_TARGET, MEMORY_TARGET, PROMPT_TARGET, FUNCTION_TARGET],
    fields=[VERBOSE, FUNCTION_CALL],
)

LLM_REPLY = dict(
    class_path="ix.chains.llm_chain.LLMReply",
    type="chain",
    name="LLM Reply",
    description="Chain that prompts an LLM for a text completion.",
    connectors=[LLM_TARGET, MEMORY_TARGET, PROMPT_TARGET],
    fields=[VERBOSE],
)
