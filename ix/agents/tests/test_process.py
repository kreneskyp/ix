import pytest
import json
from asgiref.sync import sync_to_async

from ix.agents.process import AgentProcess
from ix.conftest import USER_INPUT, load_fixture
from ix.task_log.models import TaskLogMessage
from ix.task_log.tests.fake import (
    fake_command_reply,
    fake_autonomous_toggle,
    fake_task,
)

NEXT_COMMAND = {"user_input": "NEXT COMMAND"}


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
class TestAgentProcessStart:
    async def test_start_task(self, mock_openai):
        """Run task for the first time with no auth to run commands"""
        await sync_to_async(load_fixture)("node_types")
        task = await sync_to_async(fake_task)()
        mock_reply = await sync_to_async(fake_command_reply)(task=task)
        await mock_reply.adelete()
        query = TaskLogMessage.objects.filter(task=task)
        count = await query.acount()
        assert count == 0
        agent_process = AgentProcess(task=task, agent=task.agent, chain=task.chain)

        return_value = await agent_process.start(USER_INPUT)
        assert return_value is True

        count = await query.acount()
        assert count == 2
        messages = [msg async for msg in query]
        think_msg = messages[0]
        thought_msg = messages[1]
        assert think_msg.content["type"] == "THINK"
        assert think_msg.content["input"] == {
            "user_input": "hello agent 1",
        }
        assert thought_msg.content["type"] == "THOUGHT"
        assert isinstance(thought_msg.content["runtime"], float)

        # disabled until this is logged again
        #  assert thought_msg.content["usage"] == {
        #      "completion_tokens": 7,
        #      "prompt_tokens": 5,
        #      "total_tokens": 12,
        #  }

    async def test_start_task_with_input(self, mock_openai):
        """
        Test that if `input` is included in inputs then it will be
        used instead of the default `user_input -> input` mapping.
        """
        await sync_to_async(load_fixture)("node_types")
        task = await sync_to_async(fake_task)()
        mock_reply = await sync_to_async(fake_command_reply)(task=task)
        await mock_reply.adelete()
        query = TaskLogMessage.objects.filter(task=task)
        count = await query.acount()
        assert count == 0
        agent_process = AgentProcess(task=task, agent=task.agent, chain=task.chain)

        inputs = {"user_input": "hello agent 1"}
        return_value = await agent_process.start(inputs)
        assert return_value is True

        count = await query.acount()
        assert count == 2
        messages = [msg async for msg in query]
        think_msg = messages[0]
        thought_msg = messages[1]
        assert think_msg.content["type"] == "THINK"
        assert think_msg.content["input"] == inputs
        assert thought_msg.content["type"] == "THOUGHT"
        assert isinstance(thought_msg.content["runtime"], float)


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
