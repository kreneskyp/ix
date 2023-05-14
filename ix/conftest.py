from typing import List
from unittest.mock import MagicMock

import pytest

from ix.agents.tests.mock_llm import MockChatOpenAI
from ix.task_log.tests.fake import fake_task, fake_task_log_msg


USER_INPUT = {"user_input": "hello agent 1"}


@pytest.fixture()
def mock_embeddings(mocker) -> List[float]:
    yield mocker.patch("ix.memory.plugin.get_embeddings", return_value=[0.1, 0.2, 0.3])


@pytest.fixture
def mock_openai(mocker):
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


@pytest.fixture
def task_log_msg(task):
    return fake_task_log_msg(task)


@pytest.fixture()
def command_output(mocker):
    """mocks write_output to capture output from `echo` command"""
    yield mocker.patch("ix.agents.tests.echo_command.write_output")
