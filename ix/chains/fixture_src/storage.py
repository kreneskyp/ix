from langchain.storage import RedisStore

from ix.api.chains.types import NodeTypeField

REDIS_STORE_CLASS_PATH = "langchain.storage.redis.RedisStore"
REDIS_STORE = {
    "class_path": REDIS_STORE_CLASS_PATH,
    "type": "store",
    "name": "Redis Store",
    "description": RedisStore.__doc__,
    "connectors": [],
    "fields": NodeTypeField.get_fields(
        RedisStore.__init__,
        include=[
            "redis_url",
            "ttl",
            "namespace",
        ],
        field_options={
            "redis_url": {
                "default": "redis://redis:6379/0",
            },
            "ttl": {
                "default": 3600,
                "type": "int",
                "input_type": "slider",
                "min": 0,
                "max": 60 * 200,
                "step": 10,
            },
        }
    ),
}


STORAGE = [
    REDIS_STORE,
]
