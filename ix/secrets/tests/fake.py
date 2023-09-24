from asgiref.sync import sync_to_async

from ix.secrets.models import Secret
from faker import Faker

from ix.ix_users.tests.fake import get_default_user

fake = Faker()


def fake_secret(**kwargs):
    """
    Fake a Secret for testing purposes.
    """
    user = kwargs.get("user", get_default_user())
    type_ = kwargs.get("type", "test_service")
    name = kwargs.get("name", "default instance")

    secret = Secret.objects.create(
        user=user,
        type=type_,
        name=name,
    )

    return secret


async def afake_secret(**kwargs):
    return await sync_to_async(fake_secret)(**kwargs)
