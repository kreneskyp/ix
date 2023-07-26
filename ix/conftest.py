import logging
from typing import Dict, Any
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
import redis
from asgiref.sync import sync_to_async
from django.core.management import call_command

from ix.agents.models import Agent
from ix.agents.tests.mock_llm import MockChatOpenAI
from ix.chains.callbacks import IxHandler
from ix.chains.loaders.context import IxContext
from ix.chains.management.commands.create_ix_v2 import (
    IX_CHAIN_V2,
)

from ix.chains.models import Chain, ChainNode, NodeType
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
)
from ix.utils.importlib import import_class

logger = logging.getLogger(__name__)


USER_INPUT = {"user_input": "hello agent 1"}


@pytest.fixture
def clean_redis():
    """Ensure redis is clean before and after tests"""
    redis_client = redis.Redis(host="redis", port=6379, db=0)
    redis_client.flushall()
    yield
    redis_client.flushall()


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
def load_chain(node_types, task, clean_redis):
    """
    yields a function for creating a mock chain. Used for generating
    mock functions for other chains and configs. The function takes a
    config object and generates a chain and nodes. The chain is then
    loaded and returned.
    """

    def _mock_chain(config: Dict[str, Any], context: IxContext = None) -> Chain:
        chain = fake_chain()
        chain_node = ChainNode.objects.create_from_config(chain, config, root=True)

        return chain_node.load(
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
    chain = await Chain.objects.aget(id=task.chain_id)

    async def _mock_chain(config: Dict[str, Any], context: IxContext = None) -> Chain:
        chain_node = await sync_to_async(ChainNode.objects.create_from_config)(
            chain, config, root=True
        )
        return await sync_to_async(chain_node.load)(
            context or IxContext(agent=agent, task=task, chain=chain)
        )

    yield _mock_chain


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
    load_fixture("node_types")
    load_fixture("ix_v2")


@pytest_asyncio.fixture
async def aix_agent(anode_types):
    """async version of ix_agent fixture"""
    await sync_to_async(call_command)("loaddata", "ix_v2")


@pytest_asyncio.fixture
async def anode_types() -> None:
    """calls manage.py loaddata node_types"""
    await sync_to_async(call_command)("loaddata", "node_types")


@pytest.fixture()
def clean_artifacts():
    """deletes all artifacts"""
    Artifact.objects.all().delete()


@pytest_asyncio.fixture
async def aclean_artifacts():
    """deletes all artifacts"""
    await Artifact.objects.all().adelete()
