from ix.chains.fixture_src.memory import SCOPED_MEMORY_FIELDS

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
