from langchain.chains.llm_symbolic_math.base import LLMSymbolicMathChain
from ix.api.chains.types import NodeTypeField
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

LLM_REPLY = dict(
    class_path="ix.chains.llm_chain.LLMReply",
    type="chain",
    name="LLM Reply",
    description="Chain that prompts an LLM for a text completion.",
    connectors=[LLM_TARGET, MEMORY_TARGET, PROMPT_TARGET],
    fields=[VERBOSE],
)

LLM_SYMBOLIC_MATH_CHAIN = {
    "class_path": "langchain.chains.llm_symbolic_math.base.LLMSymbolicMathChain.from_llm",
    "type": "chain",
    "name": "Symbolic Math Chain",
    "description": LLMSymbolicMathChain.__doc__,
    "connectors": [
        LLM_TARGET,
        MEMORY_TARGET,
        PROMPT_TARGET,
    ],
    "fields": [
        VERBOSE,
    ]
    + NodeTypeField.get_fields(
        LLMSymbolicMathChain,
        include=["input_key", "output_key"],
        field_options={
            "input_key": {
                "default": "user_input",
            }
        },
    ),
}

CHAINS = [
    LLM_CHAIN,
    LLM_REPLY,
    LLM_SYMBOLIC_MATH_CHAIN,
]
