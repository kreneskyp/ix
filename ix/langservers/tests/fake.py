from asgiref.sync import sync_to_async
import faker
from pydantic.main import BaseModel

from ix.api.langservers.types import RemoteRunnableConfig
from ix.langservers.models import LangServer

fake = faker.Faker()


class FakeInputSchema(BaseModel):
    topic: str = "parrots"


class FakeOutputSchema(BaseModel):
    baz: str = "qux"
    qux: int = 2


class FakeConfigSchema(BaseModel):
    xoo: str = "xar"
    xar: int = 3


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
                name="jokes",
                input_schema=FakeInputSchema.schema(),
                output_schema=FakeOutputSchema.schema(),
                config_schema=FakeConfigSchema(),
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
        user=kwargs.get("user", None),
        group=kwargs.get("group", None),
    )
    return langserver


async def afake_langserver(**kwargs):
    return await sync_to_async(fake_langserver)(**kwargs)
