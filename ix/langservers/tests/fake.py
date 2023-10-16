from asgiref.sync import sync_to_async
import faker
from pydantic.main import BaseModel

from ix.api.langservers.types import RemoteRunnableConfig
from ix.langservers.models import LangServer

fake = faker.Faker()


class FakeInputSchema(BaseModel):
    foo: str
    bar: int


class FakeOutputSchema(BaseModel):
    baz: str
    qux: int


def fake_langserver(**kwargs):
    name = "fake langserver!"
    description = (
        "langserver used for testing. The url is hardcoded to the docker host."
    )
    url = "http://host.docker.internal:9000"
    routes = kwargs.get(
        "routes",
        [
            RemoteRunnableConfig(
                name="test_route",
                input_schema=FakeInputSchema.schema(),
                output_schema=FakeOutputSchema.schema(),
            ).dict()
        ],
    )
    headers = kwargs.get("headers", {"mock": "test"})
    langserver = LangServer.objects.create(
        name=name,
        description=description,
        url=url,
        routes=routes,
        headers=headers,
    )
    return langserver


async def afake_langserver(**kwargs):
    return await sync_to_async(fake_langserver)(**kwargs)
