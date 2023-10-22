from asgiref.sync import sync_to_async
from pydantic.main import BaseModel

from ix.secrets.models import SecretType, Secret
from faker import Faker

from ix.ix_users.tests.fake import get_default_user

fake = Faker()


class MockAccount(BaseModel):
    """A simple schema for testing secrets"""

    api_key: str


def fake_secret_type(**kwargs) -> SecretType:
    """
    Fake a Secret Type for testing purposes.
    """
    name = kwargs.get("name", "test_service")

    secret_type = SecretType.objects.create(
        name=name,
        fields_schema=MockAccount.schema(),
        user=kwargs.get("user", get_default_user()),
        group=kwargs.get("group", None),
    )

    return secret_type


async def afake_secret_type(**kwargs) -> SecretType:
    return await sync_to_async(fake_secret_type)(**kwargs)


def get_mock_secret_type() -> SecretType:
    try:
        return SecretType.objects.get(name="mock_service")
    except SecretType.DoesNotExist:
        return fake_secret_type(name="mock_service")


async def aget_mock_secret_type() -> SecretType:
    return await sync_to_async(get_mock_secret_type)()


def fake_secret(**kwargs) -> Secret:
    """
    Fake a Secret for testing purposes.
    """
    type_id = kwargs.get("type_id", get_mock_secret_type().id)
    name = kwargs.get("name", "default instance")

    secret = Secret.objects.create(
        type_id=type_id,
        name=name,
        user=kwargs.get("user", get_default_user()),
        group=kwargs.get("group", None),
    )

    return secret


async def afake_secret(**kwargs) -> Secret:
    return await sync_to_async(fake_secret)(**kwargs)
