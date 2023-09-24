from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from faker import Faker

from ix.datasources.models import DataSource
from ix.task_log.tests.fake import fake_chain, fake_chain_node

fake = Faker()


def get_default_user():
    user_model = get_user_model()
    return user_model.objects.get()


def fake_datasource(**kwargs):
    """
    Fake a data source for testing purposes.
    """
    name = kwargs.get("name", fake.unique.name())
    user = kwargs.get("user", get_default_user())
    description = kwargs.get("description", fake.text())
    config = kwargs.get(
        "config",
        {
            "config_key": "config_value",
        },
    )

    retrieval_chain = kwargs.get("retrieval_chain", fake_chain())
    fake_chain_node(chain=retrieval_chain)

    datasource = DataSource.objects.create(
        name=name,
        user=user,
        description=description,
        config=config,
        retrieval_chain=retrieval_chain,
    )

    return datasource


async def afake_datasource(**kwargs):
    return await sync_to_async(fake_datasource)(**kwargs)
