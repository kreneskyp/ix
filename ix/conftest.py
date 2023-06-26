import logging
from typing import List, Dict, Any
from unittest.mock import MagicMock

import pytest
from django.core.management import call_command

from ix.agents.callback_manager import IxCallbackManager
from ix.agents.tests.mock_llm import MockChatOpenAI
from ix.chains.management.commands.create_ix_v2 import IX_CHAIN_V2

from ix.chains.models import Chain, ChainNode
from ix.task_log.tests.fake import (
    fake_task,
    fake_task_log_msg,
    fake_chat,
    fake_agent,
    fake_think,
    fake_chain,
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
    manager = IxCallbackManager(task)
    manager.think_msg = fake_think(task=task)
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


@pytest.fixture
def task(node_types):
    return fake_task()


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
    callback_manager = IxCallbackManager(chat.task)
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


@pytest.fixture()
def node_types() -> None:
    """calls manage.py loaddata node_types"""
    load_fixture("node_types")
    load_fixture("ix_v2")
