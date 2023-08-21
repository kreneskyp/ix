from ix.api.chains.types import NodeTypeField
from ix.chains.fixture_src.common import VERBOSE
from ix.chains.fixture_src.targets import (
    PROMPT_TARGET,
    TOOLS_TARGET,
    LLM_TARGET,
    MEMORY_TARGET,
)
from langchain.agents.agent_toolkits.conversational_retrieval.openai_functions import (
    create_conversational_retrieval_agent,
)

MAX_ITERATIONS = {
    "name": "max_iterations",
    "type": "integer",
    "default": 15,
    "nullable": True,
}

MAX_EXECUTION_TIME = {
    "name": "max_execution_time",
    "type": "float",
    "nullable": True,
}

EXECUTOR_BASE_FIELDS = [
    {
        "name": "return_intermediate_steps",
        "type": "boolean",
        "default": False,
    },
    MAX_ITERATIONS,
    MAX_EXECUTION_TIME,
    VERBOSE,
]


OPENAI_FUNCTIONS_AGENT = {
    "class_path": "ix.chains.loaders.agents.initialize_openai_functions",
    "type": "agent",
    "name": "OpenAI Function Agent",
    "description": "Agent that uses OpenAI's API to generate text.",
    "connectors": [LLM_TARGET, TOOLS_TARGET, PROMPT_TARGET, MEMORY_TARGET],
    "fields": EXECUTOR_BASE_FIELDS,
}

OPENAI_MULTIFUNCTION_AGENT = {
    "class_path": "ix.chains.loaders.agents.initialize_openai_multi_functions",
    "type": "agent",
    "name": "OpenAI Multifunction Agent",
    "description": "Agent that uses OpenAI's API to generate text.",
    "connectors": [LLM_TARGET, TOOLS_TARGET, PROMPT_TARGET, MEMORY_TARGET],
    "fields": EXECUTOR_BASE_FIELDS,
}

ZERO_SHOT_REACT_DESCRIPTION_AGENT = {
    "class_path": "ix.chains.loaders.agents.initialize_zero_shot_react_description",
    "type": "agent",
    "name": "Zero Shot React Description Agent",
    "description": "Agent that generates descriptions by taking zero-shot approach using reaction information.",
    "connectors": [LLM_TARGET, TOOLS_TARGET, PROMPT_TARGET, MEMORY_TARGET],
    "fields": EXECUTOR_BASE_FIELDS,
}

REACT_DOCSTORE_AGENT = {
    "class_path": "ix.chains.loaders.agents.initialize_react_docstore",
    "type": "agent",
    "name": "React Docstore Agent",
    "description": "Agent that interacts with the document store to obtain reaction-based information.",
    "connectors": [LLM_TARGET, TOOLS_TARGET, PROMPT_TARGET, MEMORY_TARGET],
    "fields": EXECUTOR_BASE_FIELDS,
}

SELF_ASK_WITH_SEARCH_AGENT = {
    "class_path": "ix.chains.loaders.agents.initialize_self_ask_with_search",
    "type": "agent",
    "name": "Self Ask with Search Agent",
    "description": "Agent that asks itself queries and searches for answers in a given context.",
    "connectors": [LLM_TARGET, TOOLS_TARGET, PROMPT_TARGET, MEMORY_TARGET],
    "fields": EXECUTOR_BASE_FIELDS,
}

CONVERSATIONAL_REACT_DESCRIPTION_AGENT = {
    "class_path": "ix.chains.loaders.agents.initialize_conversational_react_description",
    "type": "agent",
    "name": "Conversational React Description Agent",
    "description": "Agent that provides descriptions in a conversational manner using reaction information.",
    "connectors": [LLM_TARGET, TOOLS_TARGET, PROMPT_TARGET, MEMORY_TARGET],
    "fields": EXECUTOR_BASE_FIELDS,
}

CHAT_ZERO_SHOT_REACT_DESCRIPTION_AGENT = {
    "class_path": "ix.chains.loaders.agents.initialize_chat_zero_shot_react_description",
    "type": "agent",
    "name": "Chat Zero Shot React Description Agent",
    "description": "Agent that generates descriptions in a chat-based context using a zero-shot approach and reaction information.",
    "connectors": [LLM_TARGET, TOOLS_TARGET, PROMPT_TARGET, MEMORY_TARGET],
    "fields": EXECUTOR_BASE_FIELDS,
}

CHAT_CONVERSATIONAL_REACT_DESCRIPTION_AGENT = {
    "class_path": "ix.chains.loaders.agents.initialize_chat_conversational_react_description",
    "type": "agent",
    "name": "Chat Conversational React Description Agent",
    "description": "Agent that provides descriptions in a chat-based context in a conversational manner using reaction information.",
    "connectors": [LLM_TARGET, TOOLS_TARGET, PROMPT_TARGET, MEMORY_TARGET],
    "fields": EXECUTOR_BASE_FIELDS,
}

STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION_AGENT = {
    "class_path": "ix.chains.loaders.agents.initialize_structured_chat_zero_shot_react_description",
    "type": "agent",
    "name": "Structured Chat Zero Shot React Description Agent",
    "description": "Agent that generates descriptions in a structured chat context using a zero-shot approach and reaction information.",
    "connectors": [LLM_TARGET, TOOLS_TARGET, PROMPT_TARGET, MEMORY_TARGET],
    "fields": EXECUTOR_BASE_FIELDS,
}


CONVERSATIONAL_RETRIEVAL_AGENT = {
    "class_path": "langchain.agents.agent_toolkits.conversational_retrieval.openai_functions.create_conversational_retrieval_agent",
    "type": "agent",
    "name": "Conversational Retrieval agent",
    "description": "Agent that generates descriptions in a structured chat context using a zero-shot approach and reaction information.",
    "connectors": [LLM_TARGET, TOOLS_TARGET],
    "fields": [MAX_ITERATIONS, MAX_EXECUTION_TIME, VERBOSE]
    + NodeTypeField.get_fields(
        create_conversational_retrieval_agent,
        include=["remember_intermediate_steps" "memory_key" "max_token_limit"],
    ),
}


AGENTS = [
    OPENAI_FUNCTIONS_AGENT,
    OPENAI_MULTIFUNCTION_AGENT,
    ZERO_SHOT_REACT_DESCRIPTION_AGENT,
    REACT_DOCSTORE_AGENT,
    SELF_ASK_WITH_SEARCH_AGENT,
    CONVERSATIONAL_REACT_DESCRIPTION_AGENT,
    CHAT_ZERO_SHOT_REACT_DESCRIPTION_AGENT,
    CHAT_CONVERSATIONAL_REACT_DESCRIPTION_AGENT,
    STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION_AGENT,
    CONVERSATIONAL_RETRIEVAL_AGENT,
]
