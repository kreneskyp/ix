import logging
from copy import deepcopy
from typing import Dict, Any, List, Callable
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
import redis
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.management import call_command
from langchain.schema.runnable import Runnable

from ix.agents.models import Agent
from ix.agents.tests.mock_llm import MockChatOpenAI
from ix.chains.callbacks import IxHandler
from ix.chains.fixture_src.embeddings import OPENAI_EMBEDDINGS_CLASS_PATH
from ix.chains.loaders.context import IxContext
from ix.chains.management.commands.create_ix_v2 import (
    IX_CHAIN_V2,
)

from ix.chains.models import Chain, ChainNode, NodeType
from ix.chains.tests.mock_vector_embeddings import MOCK_VECTORSTORE_EMBEDDINGS
from ix.secrets.tests.fake import afake_secret
from ix.secrets.vault import delete_secrets_recursive
from ix.task_log.models import Artifact, Task
from ix.task_log.tests.fake import (
    fake_task,
    fake_task_log_msg,
    fake_chat,
    fake_agent,
    fake_think,
    fake_chain,
    afake_think,
    afake_task,
    afake_chain,
)
from ix.ix_users.tests.fake import get_default_user, afake_user
from ix.utils.importlib import import_class, _import_class

logger = logging.getLogger(__name__)


USER_INPUT = {"user_input": "hello agent 1"}


@pytest_asyncio.fixture
async def arequest_user(mocker):
    user = await afake_user()
    mock_get_request_user = mocker.patch("ix.api.auth._get_request_user")
    mock_get_request_user.return_value = user
    yield mock_get_request_user


@pytest_asyncio.fixture
async def arequest_admin(mocker):
    user = await afake_user(is_superuser=True)
    mock_get_request_user = mocker.patch("ix.api.auth._get_request_user")
    mock_get_request_user.return_value = user
    yield mock_get_request_user


@pytest.fixture()
def owner_filtering(settings):
    settings.OWNER_FILTERING = True
    yield


@pytest.fixture
def clean_redis():
    """Ensure redis is clean before and after tests"""
    redis_client = redis.Redis(**settings.REDIS)
    redis_client.flushall()
    yield
    redis_client.flushall()


@pytest.fixture(scope="function")
def clean_vault():
    """Fixture to clean up vault before and after each test

    If a test requires a secret it should be created during the test or in
    a fixture that applies this fixture first.
    """
    delete_secrets_recursive(settings.VAULT_BASE_PATH)
    yield
    delete_secrets_recursive(settings.VAULT_BASE_PATH)


@pytest.fixture
def mock_config_secrets():
    async def mock_config(config: dict, keys: List[str]) -> dict:
        config = deepcopy(config)
        for key in keys:
            secret = await afake_secret()
            datum = {key: config["config"][key]}
            await secret.awrite(datum)
            assert await secret.aread() == datum
            config["config"][key] = str(secret.id)
        return config

    return mock_config


@pytest.fixture
def mock_import_class(mocker):
    """Fixture for mocking import_class.

    Used to mock specific components (e.g. OpenAIEmbeddings) in tests.
    """
    original_import_class = _import_class
    mock_class_paths = {}

    def mock_fn(class_path):
        if class_path in mock_class_paths:
            return mock_class_paths[class_path]
        else:
            return original_import_class(class_path)

    def add_mock_path(class_path, mock_result):
        mock_class_paths[class_path] = mock_result

    mocker.patch("ix.utils.importlib._import_class", side_effect=mock_fn)
    return add_mock_path


@pytest.fixture
def mock_openai_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "MOCK_KEY")


MOCKABLE_LLM_CLASSES = [
    "langchain.chat_models.openai.ChatOpenAI",
]


@pytest.fixture
def mock_openai(mocker, mock_openai_key):
    # create a mock instance of the class
    mock_llm = MockChatOpenAI()
    mock_llm.return_value = "mock llm response"

    async def _mock_acompletion_with_retry(*args, **kwargs):
        if mock_llm.raise_exception:
            raise mock_llm.raise_exception
        content = await sync_to_async(mock_llm.get_mock_content)()
        return content

    # async completions are outside the class and need to be mocked separately
    mock_acomplete = mocker.patch("langchain.chat_models.openai.acompletion_with_retry")
    mock_acomplete.side_effect = _mock_acompletion_with_retry
    mock_llm.acompletion_with_retry = mock_acomplete

    # mock the class to return the instance we're creating here
    mock_class = MagicMock(return_value=mock_llm)

    def mock_import_class(class_path):
        if class_path in MOCKABLE_LLM_CLASSES:
            return mock_class
        else:
            return import_class(class_path)

    # mock_import returns the mock class
    mocker.patch(
        "ix.chains.loaders.core.import_node_class", side_effect=mock_import_class
    )

    # return the mock instance
    yield mock_llm


@pytest.fixture
def mock_openai_streaming(mocker, mock_openai_key):
    # create a mock instance of the class
    mock_llm = MockChatOpenAI()
    mock_llm.return_value = "mock llm response"

    async def _mock_acompletion_with_retry(*args, **kwargs):
        if mock_llm.raise_exception:
            raise mock_llm.raise_exception
        if mock_llm.streaming:
            content = mock_llm.return_value
            split = content.split(" ")
            words = []
            for split_word in split[:-1]:
                words.append(split_word)
                words.append(" ")
            words.append(split[-1])
            for word in words:
                yield {
                    "choices": [
                        {
                            "delta": {
                                "role": "system",
                                "content": word,
                                "function_call": None,
                            }
                        }
                    ]
                }

    # async completions are outside the class and need to be mocked separately
    mock_acomplete = mocker.patch("langchain.chat_models.openai.acompletion_with_retry")
    mock_acomplete.side_effect = _mock_acompletion_with_retry
    mock_llm.acompletion_with_retry = mock_acomplete

    # mock the class to return the instance we're creating here
    mock_class = MagicMock(return_value=mock_llm)

    def mock_import_class(class_path):
        if class_path in MOCKABLE_LLM_CLASSES:
            return mock_class
        else:
            return import_class(class_path)

    # mock_import returns the mock class
    mocker.patch(
        "ix.chains.loaders.core.import_node_class", side_effect=mock_import_class
    )

    # return the mock instance
    yield mock_llm


def fake_embeddings(n: int = 1) -> List[List[float]]:
    """Fake a list of embeddings."""
    return [[0.5 for x in range(1536)] for n in range(n)]


@pytest.fixture
def mock_openai_embeddings(mock_import_class, mock_openai_key):
    """Mocks OpenAIEmbeddings to return a mock response

    The mock embedding was generated for files test_data/documents
    with the real OpenAIEmbeddings component
    """
    mock_class = MagicMock()
    mock_class.instance = mock_class()
    mock_class.instance.embed_documents.return_value = MOCK_VECTORSTORE_EMBEDDINGS
    mock_class.instance.embed_query.return_value = fake_embeddings(n=1)[0]
    mock_import_class(OPENAI_EMBEDDINGS_CLASS_PATH, mock_class)
    yield mock_class.instance


@pytest.fixture
def ix_context(task):
    return IxContext(agent=task.agent, chain=task.chain, task=task)


@pytest_asyncio.fixture
async def aix_context(atask):
    agent = await Agent.objects.aget(id=atask.agent_id)
    chain = await Chain.objects.aget(id=atask.chain_id)
    yield IxContext(agent=agent, chain=chain, task=atask)


@pytest.fixture
def ix_handler(chat):
    chat = chat["chat"]
    task = Task.objects.get(id=chat.task_id)
    agent = Agent.objects.get(id=task.agent_id)
    chain = Chain.objects.get(id=task.chain_id)
    handler = IxHandler(agent=agent, chain=chain, task=task)
    handler.parent_think_msg = fake_think(task=task)
    yield handler


@pytest_asyncio.fixture
async def aix_handler(achat):
    chat = achat["chat"]
    task = await Task.objects.aget(id=chat.task_id)
    agent = await Agent.objects.aget(id=task.agent_id)
    chain = await Chain.objects.aget(id=task.chain_id)
    handler = IxHandler(agent=agent, chain=chain, task=task)
    handler.parent_think_msg = await afake_think(task=task)
    yield handler


@pytest.fixture
def mock_chain(mocker):
    """
    Mocks the function that MockChain calls. Used to hook into
    the chain and test the output.
    """
    yield mocker.patch("ix.chains.tests.mock_chain.mock_chain_func")


@pytest.fixture()
def load_chain(node_types, task, clean_redis) -> Callable[[Dict[str, Any]], Runnable]:
    """
    yields a function for creating a mock chain. Used for generating
    mock functions for other chains and configs. The function takes a
    config object and generates a chain and nodes. The chain is then
    loaded and returned.
    """

    def _mock_chain(config: Dict[str, Any], context: IxContext = None) -> Runnable:
        chain = fake_chain()
        ChainNode.objects.create_from_config(chain, config, root=True)

        return chain.load_chain(
            context or IxContext(agent=task.agent, task=task, chain=task.chain)
        )

    yield _mock_chain


@pytest_asyncio.fixture
async def aload_chain(anode_types, achat):
    """
    yields a function for creating a mock chain. Used for generating
    mock functions for other chains and configs. The function takes a
    config object and generates a chain and nodes. The chain is then
    loaded and returned.
    """

    chat = achat["chat"]
    task = await Task.objects.aget(id=chat.task_id)
    agent = await Agent.objects.aget(id=chat.lead_id)
    chain = await afake_chain()

    async def _mock_chain(config: Dict[str, Any], context: IxContext = None) -> Chain:
        await sync_to_async(ChainNode.objects.create_from_config)(
            chain, config, root=True
        )
        return await chain.aload_chain(
            context or IxContext(agent=agent, task=task, chain=chain)
        )

    yield _mock_chain


@pytest.fixture
def user():
    return get_default_user()


@pytest_asyncio.fixture
async def auser():
    return await sync_to_async(get_default_user)()


@pytest.fixture
def task(node_types):
    return fake_task()


@pytest_asyncio.fixture
async def atask(anode_types):
    return await afake_task()


@pytest.fixture()
def chat(node_types, task, load_chain, mock_openai_key, ix_context, clean_redis):
    chat = fake_chat(task=task)
    fake_agent_1 = fake_agent(
        name="agent 1", alias="agent_1", purpose="to test selections"
    )
    fake_agent_2 = fake_agent(
        name="agent 2", alias="agent_2", purpose="to test selections"
    )
    chat.agents.add(fake_agent_1)
    chat.agents.add(fake_agent_2)

    # load chain
    model_instance = Chain.objects.get(pk=IX_CHAIN_V2)
    moderator = model_instance.load_chain(context=ix_context)

    yield {
        "chat": chat,
        "fake_agent_1": fake_agent_1,
        "fake_agent_2": fake_agent_2,
        "instance": moderator,
    }


@pytest_asyncio.fixture
async def achat(anode_types, atask, aix_agent, aix_context, mock_openai_key):
    chat = await sync_to_async(fake_chat)(task=atask)
    fake_agent_1 = await sync_to_async(fake_agent)(
        name="agent 1", alias="agent_1", purpose="to test selections"
    )
    fake_agent_2 = await sync_to_async(fake_agent)(
        name="agent 2", alias="agent_2", purpose="to test selections"
    )
    await chat.agents.aset([fake_agent_1, fake_agent_2])

    # load chain
    model_instance = await Chain.objects.aget(pk=IX_CHAIN_V2)
    moderator = await model_instance.aload_chain(context=aix_context)

    return {
        "chat": chat,
        "fake_agent_1": fake_agent_1,
        "fake_agent_2": fake_agent_2,
        "instance": moderator,
    }


@pytest.fixture
def task_log_msg(task):
    return fake_task_log_msg(task)


@pytest.fixture()
def command_output(mocker):
    """mocks write_output to capture output from `echo` command"""
    yield mocker.patch("ix.agents.tests.echo_command.write_output")


def load_fixture(fixture: str) -> None:
    """calls manage.py loaddata"""
    call_command("loaddata", fixture)


aload_fixture = sync_to_async(load_fixture)


@pytest.fixture()
def node_types() -> None:
    """calls manage.py loaddata node_types"""
    NodeType.objects.all().delete()
    Chain.objects.all().delete()
    call_command("import_langchain")
    load_fixture("agent/ix")


@pytest_asyncio.fixture
async def aix_agent(anode_types):
    """async version of ix_agent fixture"""
    await sync_to_async(call_command)("loaddata", "agent/ix")
    await sync_to_async(call_command)("loaddata", "agent/code")
    await sync_to_async(call_command)("loaddata", "agent/readme")


@pytest_asyncio.fixture
async def anode_types() -> None:
    """calls manage.py loaddata node_types"""
    await sync_to_async(call_command)("import_langchain")


@pytest.fixture()
def clean_artifacts():
    """deletes all artifacts"""
    Artifact.objects.all().delete()


@pytest_asyncio.fixture
async def aclean_artifacts():
    """deletes all artifacts"""
    await Artifact.objects.all().adelete()
