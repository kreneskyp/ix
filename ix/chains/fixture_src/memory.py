from ix.chains.fixture_src.targets import (
    MEMORY_BACKEND_TARGET,
    LLM_TARGET,
    PROMPT_TARGET,
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
        "label": "Session Scope",
        "type": "string",
        "input_type": "select",
        "choices": [
            {"label": "chat", "value": "chat"},
            {"label": "agent", "value": "agent"},
            {"label": "task", "value": "task"},
            {"label": "user", "value": "user"},
        ],
        "style": {"width": "100%"},
    },
    {
        "name": "session_prefix",
        "label": "Session Prefix",
        "description": "prefix applied to the session ID. e.g. 'chat' will result in 'chat:session_id'."
        "Chains with the same scope and prefix will share the same session.",
        "type": "string",
        "default": "",
        "style": {"width": "100%"},
    },
    {
        "name": "session_key",
        "label": "Session Key",
        "description": "component session will be initialized with this argument.",
        "type": "string",
        "default": "session_id",
        "style": {"width": "100%"},
    },
]
SCOPED_MEMORY_FIELD_GROUP = {
    "key": "Session",
    "fields": ["session_scope", "session_prefix", "session_key"],
}


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
