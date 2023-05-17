from typing import List
from unittest.mock import MagicMock

import pytest

from ix.agents.callback_manager import IxCallbackManager
from ix.agents.tests.mock_llm import MockChatOpenAI
from ix.chains.moderator import ChatModerator
from ix.task_log.tests.fake import (
    fake_task,
    fake_task_log_msg,
    fake_chat,
    fake_agent,
    fake_think,
)

USER_INPUT = {"user_input": "hello agent 1"}


@pytest.fixture()
def mock_embeddings(mocker) -> List[float]:
    yield mocker.patch("ix.memory.plugin.get_embeddings", return_value=[0.1, 0.2, 0.3])


@pytest.fixture
def mock_openai_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "MOCK_KEY")


@pytest.fixture
def mock_openai(mocker, mock_openai_key):
    # create a mock instance of the class
    mock_llm = MockChatOpenAI()

    # mock the class to return the instance we're creating here
    mock_class = MagicMock(return_value=mock_llm)

    # mock_import returns the mock class
    mock_import = mocker.patch("ix.agents.llm.import_llm_class")
    mock_import.return_value = mock_import.return_value = mock_class

    # return the mock instance
    yield mock_llm


@pytest.fixture
def task():
    return fake_task()


@pytest.fixture()
def chat(mock_openai_key):
    chat = fake_chat()
    fake_agent_1 = fake_agent(
        name="agent 1", alias="agent_1", purpose="to test selections"
    )
    fake_agent_2 = fake_agent(
        name="agent 2", alias="agent_2", purpose="to test selections"
    )
    chat.agents.set([fake_agent_1, fake_agent_2])
    callback_manager = IxCallbackManager(chat.task)
    callback_manager.think_msg = fake_think(task=chat.task)

    config = {
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
            "config": {"request_timeout": 120, "temperature": 0.2, "verbose": True},
        }
    }

    yield {
        "chat": chat,
        "fake_agent_1": fake_agent_1,
        "fake_agent_2": fake_agent_2,
        "instance": ChatModerator.from_config(
            config, callback_manager=callback_manager
        ),
    }


@pytest.fixture
def task_log_msg(task):
    return fake_task_log_msg(task)


@pytest.fixture()
def command_output(mocker):
    """mocks write_output to capture output from `echo` command"""
    yield mocker.patch("ix.agents.tests.echo_command.write_output")
