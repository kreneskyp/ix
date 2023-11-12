from ix.api.components.types import NodeTypeField
from ix.chains.components.memory import LoadMemory, SaveMemory
from ix.chains.fixture_src.targets import (
    MEMORY_BACKEND_TARGET,
    LLM_TARGET,
    PROMPT_TARGET, MEMORY_TARGET,
)

MEMORY_KEY = {
    "name": "memory_key",
    "type": "string",
    "default": "history",
}

HUMAN_PREFIX = {
    "name": "human_prefix",
    "type": "string",
    "default": "Human",
}

AI_PREFIX = {
    "name": "ai_prefix",
    "type": "string",
    "default": "AI",
}

SCOPED_MEMORY_FIELDS = [
    {
        "name": "session_scope",
        "type": "string",
        "input_type": "select",
        "choices": [
            {"label": "chat", "value": "chat"},
            {"label": "agent", "value": "agent"},
            {"label": "task", "value": "task"},
            {"label": "user", "value": "user"},
        ],
    },
    {
        "name": "session_prefix",
        "type": "string",
        "default": "",
    },
    {
        "name": "session_key",
        "type": "string",
        "default": "session_id",
    },
]


CHAT_MEMORY_FIELDS = [
    {
        "name": "output_key",
        "type": "string",
        "default": "output",
    },
    {
        "name": "input_key",
        "type": "string",
        "default": "input",
    },
    {
        "name": "return_messages",
        "type": "boolean",
        "default": False,
    },
]

CONVERSATION_BUFFER_MEMORY = {
    "class_path": "langchain.memory.ConversationBufferMemory",
    "type": "memory",
    "name": "Conversation Buffer",
    "description": "Memory that stores conversation history as a buffer.",
    "connectors": [MEMORY_BACKEND_TARGET],
    "fields": [MEMORY_KEY, HUMAN_PREFIX, AI_PREFIX] + CHAT_MEMORY_FIELDS,
}

CONVERSATION_TOKEN_BUFFER_MEMORY = {
    "class_path": "langchain.memory.token_buffer.ConversationTokenBufferMemory",
    "type": "memory",
    "name": "Conversation Token Buffer",
    "description": "Memory that stores conversation history as a buffer with a max token size.",
    "connectors": [MEMORY_BACKEND_TARGET, LLM_TARGET],
    "fields": [
        {
            "name": "max_token_limit",
            "type": "number",
            "default": 2000,
        },
        MEMORY_KEY,
        HUMAN_PREFIX,
        AI_PREFIX,
    ]
    + CHAT_MEMORY_FIELDS,
}

CONVERSATION_SUMMARY_BUFFER_MEMORY = {
    "class_path": "langchain.memory.summary_buffer.ConversationSummaryBufferMemory",
    "type": "memory",
    "name": "Conversation Summary Buffer",
    "description": "Memory that stores conversation history as a buffer and summarizes to compress context.",
    "connectors": [MEMORY_BACKEND_TARGET, LLM_TARGET, PROMPT_TARGET],
    "fields": [
        {
            "name": "max_token_limit",
            "type": "number",
            "default": 2000,
        },
        MEMORY_KEY,
        HUMAN_PREFIX,
        AI_PREFIX,
    ]
    + CHAT_MEMORY_FIELDS,
}

CONVERSATION_BUFFER_WINDOW_MEMORY = {
    "class_path": "langchain.memory.buffer_window.ConversationBufferWindowMemory",
    "type": "memory",
    "name": "Conversation Buffer Window",
    "description": "Memory that stores conversation history as a buffer and summarizes to compress context.",
    "connectors": [MEMORY_BACKEND_TARGET],
    "fields": [
        {
            "name": "k",
            "label": "Window Size",
            "type": "number",
            "default": 5,
        },
        MEMORY_KEY,
        HUMAN_PREFIX,
        AI_PREFIX,
    ]
    + CHAT_MEMORY_FIELDS,
}

LOAD_MEMORY_CLASS_PATH = "ix.chains.components.memory.LoadMemory"
LOAD_MEMORY = {
    "class_path": LOAD_MEMORY_CLASS_PATH,
    "type": "chain",
    "name": "Load Memories",
    "description": "Load memories from short term storage for use in a prompt.",
    "connectors": [MEMORY_TARGET],
    "fields": NodeTypeField.get_fields(
        LoadMemory,
        include=["output_key", "memory_inputs"],
        field_options={
            "memory_inputs": {
                "type": "list",
           },
        },
    ),
}

SAVE_MEMORY_CLASS_PATH = "ix.chains.components.memory.SaveMemory"
SAVE_MEMORY = {
    "class_path": SAVE_MEMORY_CLASS_PATH,
    "type": "chain",
    "name": "Save Memories",
    "description": "Save memories to short term storage.",
    "connectors": [MEMORY_TARGET],
    "fields": NodeTypeField.get_fields(
        SaveMemory,
        include=["input_keys", "output_keys"],
        field_options={
            "input_keys": {
                "type": "list",
            },
            "output_keys": {
                "type": "list",
           },
        },
    ),
}

MEMORY = [
    CONVERSATION_BUFFER_MEMORY,
    CONVERSATION_TOKEN_BUFFER_MEMORY,
    CONVERSATION_SUMMARY_BUFFER_MEMORY,
    CONVERSATION_BUFFER_WINDOW_MEMORY,
    LOAD_MEMORY,
    SAVE_MEMORY,
]
