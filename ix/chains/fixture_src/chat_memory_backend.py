from ix.chains.fixture_src.memory import SCOPED_MEMORY_FIELDS, SCOPED_MEMORY_FIELD_GROUP

REDIS_MEMORY_BACKEND = {
    "class_path": "langchain.memory.RedisChatMessageHistory",
    "type": "memory_backend",
    "name": "Redis Memory Backend",
    "description": "Redis Memory Backend",
    "fields": [
        {
            "name": "url",
            "type": "string",
            "default": "redis://redis:6379/0",
            "style": {"width": "100%"},
        },
        {
            "name": "ttl",
            "type": "number",
            "default": 3600,
        },
    ]
    + SCOPED_MEMORY_FIELDS,
}


FILESYSTEM_MEMORY_BACKEND = {
    "class_path": "langchain.memory.chat_message_histories.file.FileChatMessageHistory",
    "type": "memory_backend",
    "name": "Filesystem Memory Backend",
    "description": "Stores memories in a local file",
    "fields": [
        {
            "name": "file_path",
            "type": "string",
            "default": "/var/app/workdir/chat_memory.txt",
            "style": {"width": "100%"},
        },
    ],
}


POSTGRES_CHAT_HISTORY_CLASS_PATH = (
    "langchain.memory.chat_message_histories.postgres.PostgresChatMessageHistory"
)
POSTGRES_CHAT_HISTORY = {
    "class_path": POSTGRES_CHAT_HISTORY_CLASS_PATH,
    "type": "memory_backend",
    "name": "Postgres Chat History",
    "description": "Stores chat history in a Postgres database",
    "display_groups": [
        {
            "key": "Database",
            "fields": ["connection_string", "table_name"],
        },
        SCOPED_MEMORY_FIELD_GROUP,
    ],
    "fields": [
        {
            "name": "connection_string",
            "label": "Connection String",
            "type": "string",
            "default": "postgresql://ix:ix@db:5432/ix",
            "style": {"width": "100%"},
        },
        {
            "name": "table_name",
            "type": "string",
            "default": "message_store",
            "style": {"width": "100%"},
        },
    ]
    + SCOPED_MEMORY_FIELDS,
}

MEMORY_BACKEND = [
    REDIS_MEMORY_BACKEND,
    FILESYSTEM_MEMORY_BACKEND,
    POSTGRES_CHAT_HISTORY,
]
