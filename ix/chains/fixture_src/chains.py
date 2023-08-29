from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.base import (
    BaseConversationalRetrievalChain,
)
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
    RETRIEVER_TARGET,
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

BASE_CONVERSATIONAL_RETRIEVAL_CHAIN_FIELDS = NodeTypeField.get_fields(
    BaseConversationalRetrievalChain,
    include=[
        "output_key",
        "rephrase_question",
        "return_source_documents",
        "return_generated_question",
    ],
)


CONVERSATIONAL_RETRIEVAL_CHAIN_CLASS_PATH = "langchain.chains.conversational_retrieval.base.ConversationalRetrievalChain.from_llm"
CONVERSATIONAL_RETRIEVAL_CHAIN = {
    "class_path": CONVERSATIONAL_RETRIEVAL_CHAIN_CLASS_PATH,
    "type": "chain",
    "name": "ConversationalRetrievalChain",
    "description": "Chain for having a conversation based on retrieved documents.",
    "connectors": [
        LLM_TARGET,
        MEMORY_TARGET,
        PROMPT_TARGET,
        RETRIEVER_TARGET,
    ],
    "fields": [
        VERBOSE,
    ]
    + BASE_CONVERSATIONAL_RETRIEVAL_CHAIN_FIELDS
    + NodeTypeField.get_fields(
        ConversationalRetrievalChain,
        include=["max_tokens_limit"],
    ),
}

CHAINS = [LLM_CHAIN, LLM_REPLY, LLM_SYMBOLIC_MATH_CHAIN, CONVERSATIONAL_RETRIEVAL_CHAIN]
__all__ = ["CHAINS"]
