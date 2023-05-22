from typing import List

import pytest
import json

from ix.agents.exceptions import AgentQuestion
from ix.agents.process import AgentProcess
from ix.conftest import USER_INPUT
from ix.task_log.models import TaskLogMessage
from ix.task_log.tests.fake import (
    fake_command_reply,
    fake_feedback_request,
    fake_feedback,
    fake_autonomous_toggle,
    fake_think,
)


NEXT_COMMAND = {"user_input": "NEXT COMMAND"}


@pytest.fixture()
def mock_embeddings(mocker) -> List[float]:
    yield mocker.patch("ix.memory.redis.get_embeddings", return_value=[0.1, 0.2, 0.3])


class MockTicker:
    """Mock tick method used for testing autonomous mode without risking infinite loops"""

    def __init__(self, agent_process, task, return_value=None):
        # limit runs to less than loop n
        self.remaining = 3
        self.task = task
        self.agent_process = agent_process
        self.executes = []
        self.return_value = return_value

    def __call__(self, user_input: str = "Next Command", execute: bool = False):
        self.executes.append(execute)
        self.remaining -= 1
        # use toggle to stop autonomous mode
        if not self.remaining:
            fake_autonomous_toggle(task=self.task, enabled=0)

        # simulate return code, will be False when autonomous mode
        # is disabled and agent returns with AUTH_REQUEST
        if self.return_value is not None:
            return self.return_value
        return self.remaining >= 0


class MessageTeardown:
    def teardown_method(self):
        # always teardown to prevent leaks when django_db doesnt clear db
        TaskLogMessage.objects.all().delete()


@pytest.mark.django_db
class TestAgentProcessInit:
    def test_init_with_defaults(self, task):
        agent_process = AgentProcess(task_id=task.id, chain_id=task.chain.id)
        assert agent_process.task_id == task.id


@pytest.mark.django_db
class TestAgentProcessStart:
    def test_start_task(self, task, mock_openai, mock_embeddings):
        """Run task for the first time with no auth to run commands"""
        mock_reply = fake_command_reply(task=task)
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(task_id=task.id, chain_id=task.chain.id)
        mock_openai.return_value = msg_to_response(mock_reply)
        return_value = agent_process.start(USER_INPUT)
        assert return_value is True
        assert query.count() == 2

        think_msg = query[0]
        thought_msg = query[1]
        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"

    def test_restart_task_with_feedback(self, task, mock_openai, mock_embeddings):
        """
        Restarting the feedback will trigger a THINK
        """

        # TODO: test injection of feedback into loop, i.e. is it in context
        mock_reply = fake_command_reply()
        mock_feedback = fake_feedback(task=task, message_id=mock_reply.id)
        query = TaskLogMessage.objects.filter(
            task=task, created_at__gt=mock_feedback.created_at
        )
        assert query.count() == 0

        agent_process = AgentProcess(task_id=task.id, chain_id=task.chain.id)
        mock_openai.return_value = msg_to_response(mock_reply)

        # start process
        return_value = agent_process.start(USER_INPUT)
        assert return_value is True
        assert query.count() == 2
        think_msg = query[0]
        thought_msg = query[1]

        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"

    def test_loop_exit_on_tick_false(self, task, mock_openai):
        """
        Test that the loop exits when tick returns False. This mechanism allows
        tick to signal to the loop that it should exit even if the loop has not
        yet reached the maximum number of ticks or is in autonomous mode.
        """
        fake_autonomous_toggle(task=task, enabled=1)
        agent_process = AgentProcess(task_id=task.id, chain_id=task.chain.id)
        agent_process.tick = MockTicker(agent_process, task, return_value=False)
        return_value = agent_process.start(n=3)
        assert return_value is False
        # only the first tick should have executed
        assert agent_process.tick.executes == [1]


def msg_to_response(msg: TaskLogMessage):
    """utility for turning model instances back into response json"""
    content = dict(msg.content.items())
    content.pop("type")
    json_content = f"###START###{json.dumps(content, sort_keys=True)}###END###"
    return json_content

    return {
        "choices": [{"message": {"content": json_content}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 7, "total_tokens": 12},
    }


@pytest.mark.django_db
class TestAgentProcessTicks:
    def test_tick_user_input_without_auth(self, task, mock_openai, mock_embeddings):
        """
        Test ticking for NEXT_COMMAND where the user has not granted
        authentication to execute the command autonomously.

        Should result in agent message for command and auth_request
        """
        mock_reply = fake_command_reply()
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(task_id=task.id, chain_id=task.chain.id)
        mock_openai.return_value = msg_to_response(mock_reply)
        agent_process.tick(user_input={"user_input": "extra input"}, execute=False)
        assert query.count() == 2

        think_msg = query[0]
        thought_msg = query[1]
        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"

    def test_tick_user_input_with_auth(
        self, task, mock_openai, command_output, mock_embeddings
    ):
        """
        Test ticking for NEXT_COMMAND where the user has granted
        authentication to execute the command autonomously.
        """
        mock_reply = fake_command_reply()
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(task_id=task.id, chain_id=task.chain.id)
        mock_openai.return_value = msg_to_response(mock_reply)
        agent_process.tick(user_input={"user_input": "extra input"}, execute=True)

        assert query.count() == 2
        think_msg = query[0]
        thought_msg = query[1]
        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"

    def test_tick_response_with_question(self, task, mock_openai, mock_embeddings):
        """Test that question response are parsed as expected"""
        mock_reply = fake_feedback_request(task=task)
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(task_id=task.id, chain_id=task.chain.id)
        mock_openai.raise_exception = AgentQuestion("this is a fake question")
        return_value = agent_process.tick(NEXT_COMMAND, execute=True)

        # return value is False because the loop should exit even
        # if in autonomous mode. The user should be prompted to
        # answer the question before continuing.
        assert return_value is False

        assert query.count() == 3
        think_msg = query[0]
        thought_msg = query[1]
        msg_1 = query[2]

        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"
        assert msg_1.role == "assistant"
        assert msg_1.content["type"] == "FEEDBACK_REQUEST"
        assert msg_1.content["question"] == "this is a fake question"


@pytest.mark.django_db
class TestAgentProcessAIChat:
    def test_chat_with_ai(self, task, mock_openai, mock_embeddings):
        mock_reply = fake_command_reply()
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0

        think_msg = fake_think()

        mock_openai.return_value = msg_to_response(mock_reply)
        agent_process = AgentProcess(task_id=task.id, chain_id=task.chain.id)
        message = {"user_input": "Test message"}
        agent_process.chat_with_ai(think_msg, message)
        # mock_openai.assert_called()

        assert query.count() == 2
        think_msg = query[0]
        thought_msg = query[1]
        assert think_msg.content["type"] == "THINK"
        assert think_msg.content["input"] == {"user_input": "Test message"}
        assert thought_msg.content["type"] == "THOUGHT"
        assert isinstance(thought_msg.content["runtime"], float)

        # disabled until this is logged again
        #  assert thought_msg.content["usage"] == {
        #      "completion_tokens": 7,
        #      "prompt_tokens": 5,
        #      "total_tokens": 12,
        #  }
