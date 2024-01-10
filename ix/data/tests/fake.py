from asgiref.sync import sync_to_async
from pydantic import BaseModel

from ix.data.models import Schema


class FakeSchema(BaseModel):
    foo: int = 1
    bar: str = "baz"


def fake_schema(**kwargs) -> Schema:
    options = {
        "name": kwargs.get("name", "Test Schema"),
        "type": kwargs.get("type", "json"),
        "description": kwargs.get("description", "A test schema"),
        "value": kwargs.get("value", FakeSchema.model_json_schema()),
        "meta": kwargs.get("meta", {}),
    }
    return Schema.objects.create(**options)


async def afake_schema(**kwargs) -> Schema:
    return await sync_to_async(fake_schema)(**kwargs)
