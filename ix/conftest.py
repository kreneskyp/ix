import logging
from typing import List, Dict, Any
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from asgiref.sync import sync_to_async
from django.core.management import call_command

from ix.agents.callback_manager import IxCallbackManager
from ix.agents.models import Agent
from ix.agents.tests.mock_llm import MockChatOpenAI
from ix.chains.management.commands.create_ix_v2 import (
    IX_CHAIN_V2,
)

from ix.chains.models import Chain, ChainNode
from ix.task_log.models import Artifact
from ix.task_log.tests.fake import (
    fake_task,
    fake_task_log_msg,
    fake_chat,
    fake_agent,
    fake_think,
    fake_chain,
    afake_think,
    afake_chat,
    afake_task,
)
from ix.utils.importlib import import_class

logger = logging.getLogger(__name__)


USER_INPUT = {"user_input": "hello agent 1"}


@pytest.fixture()
def mock_embeddings(mocker) -> List[float]:
    yield mocker.patch("ix.memory.plugin.get_embeddings", return_value=[0.1, 0.2, 0.3])


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
def mock_callback_manager(task):
    fake_chat(task=task)
    manager = IxCallbackManager(task, task.agent)
    manager.think_msg = fake_think(task=task)
    yield manager


@pytest.fixture
async def amock_callback_manager(atask):
    await afake_chat(task=atask)
    agent = await Agent.objects.aget(id=atask.agent_id)
    manager = IxCallbackManager(atask, agent)
    manager.think_msg = await afake_think(task=atask)
    yield manager


@pytest.fixture
def mock_chain(mocker):
    """
    Mocks the function that MockChain calls. Used to hook into
    the chain and test the output.
    """
    yield mocker.patch("ix.chains.tests.mock_chain.mock_chain_func")


@pytest.fixture()
def load_chain(node_types, mock_callback_manager):
    """
    yields a function for creating a mock chain. Used for generating
    mock functions for other chains and configs. The function takes a
    config object and generates a chain and nodes. The chain is then
    loaded and returned.
    """

    def _mock_chain(
        config: Dict[str, Any], callback_manager: IxCallbackManager = None
    ) -> Chain:
        chain = fake_chain()
        chain_node = ChainNode.objects.create_from_config(chain, config, root=True)
        return chain_node.load(callback_manager or mock_callback_manager)

    yield _mock_chain


@pytest_asyncio.fixture
async def aload_chain(anode_types, amock_callback_manager):
    """
    yields a function for creating a mock chain. Used for generating
    mock functions for other chains and configs. The function takes a
    config object and generates a chain and nodes. The chain is then
    loaded and returned.
    """

    def _mock_chain(
        config: Dict[str, Any], callback_manager: IxCallbackManager = None
    ) -> Chain:
        chain = fake_chain()
        chain_node = ChainNode.objects.create_from_config(chain, config, root=True)
        return chain_node.load(callback_manager or amock_callback_manager)

    yield sync_to_async(_mock_chain)


@pytest.fixture
def task(node_types):
    return fake_task()


@pytest_asyncio.fixture
async def atask(anode_types):
    return await afake_task()


@pytest.fixture()
def chat(node_types, task, load_chain, mock_openai_key):
    chat = fake_chat(task=task)
    fake_agent_1 = fake_agent(
        name="agent 1", alias="agent_1", purpose="to test selections"
    )
    fake_agent_2 = fake_agent(
        name="agent 2", alias="agent_2", purpose="to test selections"
    )
    chat.agents.set([fake_agent_1, fake_agent_2])
    callback_manager = IxCallbackManager(chat.task, agent=chat.lead)
    callback_manager.think_msg = fake_think(task=chat.task)

    # load chain
    model_instance = Chain.objects.get(pk=IX_CHAIN_V2)
    moderator = model_instance.load_chain(callback_manager)

    yield {
        "chat": chat,
        "fake_agent_1": fake_agent_1,
        "fake_agent_2": fake_agent_2,
        "instance": moderator,
    }


@pytest_asyncio.fixture
async def achat(atask, aix_agent):
    chat = await sync_to_async(fake_chat)(task=atask)
    fake_agent_1 = await sync_to_async(fake_agent)(
        name="agent 1", alias="agent_1", purpose="to test selections"
    )
    fake_agent_2 = await sync_to_async(fake_agent)(
        name="agent 2", alias="agent_2", purpose="to test selections"
    )
    await chat.agents.aset([fake_agent_1, fake_agent_2])
    lead = await Agent.objects.aget(pk=chat.lead_id)
    callback_manager = IxCallbackManager(atask, agent=lead)
    callback_manager.think_msg = await sync_to_async(fake_think)(task=atask)

    # load chain
    model_instance = await Chain.objects.aget(pk=IX_CHAIN_V2)
    moderator = await model_instance.aload_chain(callback_manager)

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
    load_fixture("node_types")
    load_fixture("ix_v2")


@pytest_asyncio.fixture
async def aix_agent():
    """async version of ix_agent fixture"""
    await sync_to_async(call_command)("loaddata", "ix_v2")


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
