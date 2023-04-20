from typing import List
from unittest.mock import call

import pytest
import json
from ix.agents.process import AgentProcess, DEFAULT_COMMANDS, DEFAULT_MEMORY
from ix.memory.redis import RedisVectorMemory
from ix.task_log.models import TaskLogMessage
from ix.task_log.tests.fake import (
    fake_task,
    fake_task_log_msg,
    fake_command_reply,
    fake_authorize,
    fake_feedback_request,
    fake_feedback,
    fake_autonomous_toggle,
    fake_task_log_msg_type,
)


@pytest.fixture
def task():
    return fake_task()


@pytest.fixture
def task_log_msg(task):
    return fake_task_log_msg(task)


@pytest.fixture
def mock_openai(mocker):
    mock_openai = mocker.patch("ix.agents.process.openai", autospec=True)
    yield mock_openai.ChatCompletion.create


@pytest.fixture()
def command_output(mocker):
    """mocks write_output to capture output from `echo` command"""
    yield mocker.patch("ix.agents.tests.echo_command.write_output")


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

    def __call__(
        self, user_input: str = AgentProcess.NEXT_COMMAND, execute: bool = False
    ):
        self.executes.append(execute)
        self.remaining -= 1
        # use toggle to stop autonomous mode
        if not self.remaining:
            fake_autonomous_toggle(task=self.task, enabled=0)
            self.agent_process.update_message_history()

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
        agent_process = AgentProcess(task_id=task.id)
        assert agent_process.task_id == task.id
        assert agent_process.memory_class == DEFAULT_MEMORY
        assert agent_process.command_modules == DEFAULT_COMMANDS


@pytest.mark.django_db
class TestAgentProcessHistory(MessageTeardown):
    MSG_1 = {"type": "COMMAND", "message": "THIS IS A TEST 1"}
    MSG_2 = {"type": "COMMAND", "message": "THIS IS A TEST 2"}
    MSG_3 = {"type": "COMMAND", "message": "THIS IS A TEST 3"}
    MSG_4 = {"type": "COMMAND", "message": "THIS IS A TEST 4"}

    @pytest.mark.parametrize("content_type", AgentProcess.EXCLUDED_MSG_TYPES)
    def test_query_message_excludes_msgs(self, content_type, task):
        """Test that non-relevant messages are excluded from history"""
        msg = fake_task_log_msg_type(content_type, task=task)
        agent_process = AgentProcess(task_id=task.id)
        agent_process.update_message_history()

        for history_msg in agent_process.history:
            assert history_msg != msg.as_message()

    @pytest.mark.parametrize(
        "content_type", ["FEEDBACK", "COMMAND", "EXECUTED", "EXECUTE_ERROR"]
    )
    def test_query_message_includes_types(self, content_type, task):
        """Test that relevant messages are included in history"""
        msg = fake_task_log_msg_type(content_type, task=task)
        agent_process = AgentProcess(task_id=task.id)
        agent_process.update_message_history()
        assert len(agent_process.history) >= 1
        assert agent_process.history[-1] == msg.as_message()

    def test_query_message_history_without_since(self, task):
        """Test querying all messages"""
        msg1 = fake_task_log_msg(task=task)
        msg2 = fake_task_log_msg(task=task)
        agent_process = AgentProcess(task_id=task.id)
        messages = agent_process.query_message_history()
        assert messages.count() == 2
        assert messages.filter(id=msg1.id).exists()
        assert messages.filter(id=msg2.id).exists()

    def test_query_message_history_with_since(self, task):
        """Test querying new messages"""
        msg1 = fake_task_log_msg(task=task)
        msg2 = fake_task_log_msg(task=task)
        agent_process = AgentProcess(task_id=task.id)
        messages = agent_process.query_message_history(since=msg1.created_at)
        assert messages.count() == 1
        assert not messages.filter(id=msg1.id).exists()
        assert messages.filter(id=msg2.id).exists()

    def test_update_message_history_no_messages(self, task):
        """initializing history before there are messages"""
        agent_process = AgentProcess(task_id=task.id)
        assert len(agent_process.history) == 0

        # still no messages
        agent_process.update_message_history()
        assert len(agent_process.history) == 0

        # first update
        msg1 = fake_command_reply(task=task)
        msg2 = fake_command_reply(task=task)
        agent_process.update_message_history()
        assert len(agent_process.history) == 2
        assert agent_process.history[0] == msg1.as_message()
        assert agent_process.history[1] == msg2.as_message()

    def test_update_message_history_with_messages(self, task):
        """initialize history when there are messages"""
        assert not TaskLogMessage.objects.all().exists()
        msg1 = fake_task_log_msg(task=task, content=self.MSG_1).as_message()
        msg2 = fake_task_log_msg(task=task, content=self.MSG_2).as_message()
        agent_process = AgentProcess(task_id=task.id)
        agent_process.update_message_history()
        assert len(agent_process.history) == 2
        assert agent_process.history[0] == msg1
        assert agent_process.history[1] == msg2

        # updating with no new messages
        agent_process.update_message_history()
        assert len(agent_process.history) == 2
        assert agent_process.history[0] == msg1
        assert agent_process.history[1] == msg2

        # add more messages and update
        msg3 = fake_task_log_msg(task=task, content=self.MSG_3).as_message()
        msg4 = fake_task_log_msg(task=task, content=self.MSG_4).as_message()
        agent_process.update_message_history()
        assert len(agent_process.history) == 4
        assert agent_process.history[0] == msg1
        assert agent_process.history[1] == msg2
        assert agent_process.history[2] == msg3
        assert agent_process.history[3] == msg4

    def test_continuous_toggle(self, task, mock_openai, command_output):
        """Can enable/disable autonomous mode"""
        assert not TaskLogMessage.objects.all().exists()
        fake_task_log_msg(task=task, content=self.MSG_1)
        fake_task_log_msg(task=task, content=self.MSG_2)
        agent_process = AgentProcess(task_id=task.id)
        agent_process.update_message_history()
        assert not agent_process.autonomous

        # toggle autonomous to enabled
        fake_autonomous_toggle(enabled=1)
        agent_process.update_message_history()
        assert agent_process.autonomous

        # toggle autonomous to disabled
        fake_autonomous_toggle(enabled=0)
        agent_process.update_message_history()
        assert not agent_process.autonomous

        # toggle autonomous to enabled
        fake_autonomous_toggle(enabled=1)
        agent_process.update_message_history()
        assert agent_process.autonomous

        # toggle autonomous to disabled
        fake_autonomous_toggle(enabled=0)
        agent_process.update_message_history()
        assert not agent_process.autonomous

    def test_autonomous_toggle_latest(self, task):
        """only latest toggle is used"""
        assert not TaskLogMessage.objects.all().exists()
        fake_task_log_msg(task=task, content=self.MSG_1)
        fake_task_log_msg(task=task, content=self.MSG_2)
        agent_process = AgentProcess(task_id=task.id)
        agent_process.update_message_history()
        assert not agent_process.autonomous

        # verify it uses latest with many back and forth
        fake_autonomous_toggle(enabled=1)
        fake_autonomous_toggle(enabled=0)
        fake_autonomous_toggle(enabled=1)
        fake_autonomous_toggle(enabled=1)
        fake_autonomous_toggle(enabled=0)
        agent_process.update_message_history()
        assert not agent_process.autonomous

        # verify it uses latest
        fake_autonomous_toggle(enabled=0)
        fake_autonomous_toggle(enabled=1)
        agent_process.update_message_history()
        assert agent_process.autonomous

        # verify it uses latest
        fake_autonomous_toggle(enabled=1)
        fake_autonomous_toggle(enabled=0)
        agent_process.update_message_history()
        assert not agent_process.autonomous

        # verify it uses latest with many back and forth
        fake_autonomous_toggle(enabled=0)
        fake_autonomous_toggle(enabled=1)
        fake_autonomous_toggle(enabled=1)
        fake_autonomous_toggle(enabled=0)
        fake_autonomous_toggle(enabled=1)
        agent_process.update_message_history()
        assert agent_process.autonomous

    def test_autonomous_toggle_interspersed(self, task, mock_openai, command_output):
        """Doesn't have to be the latest of all messages"""
        assert not TaskLogMessage.objects.all().exists()
        fake_task_log_msg(task=task, content=self.MSG_1)
        fake_task_log_msg(task=task, content=self.MSG_2)
        agent_process = AgentProcess(task_id=task.id)
        agent_process.update_message_history()
        assert not agent_process.autonomous

        fake_task_log_msg(task=task, content=self.MSG_1)
        fake_autonomous_toggle(enabled=1)
        fake_autonomous_toggle(enabled=0)
        fake_autonomous_toggle(enabled=1)
        fake_task_log_msg(task=task, content=self.MSG_1)
        agent_process.update_message_history()
        assert agent_process.autonomous


@pytest.mark.django_db
class TestAgentProcessMemory:
    def test_init_with_custom_memory_class(self, task):
        custom_memory_class = "ix.memory.tests.mock_vector_memory.MockMemory"
        assert (
            custom_memory_class != DEFAULT_MEMORY
        ), "test shouldn't use the default memory as the custom option"
        agent_process = AgentProcess(task_id=task.id, memory_class=custom_memory_class)
        assert agent_process.memory_class == custom_memory_class

    def test_initialize_memory_with_default_memory_class(self, task):
        agent_process = AgentProcess(task_id=task.id)
        assert isinstance(agent_process.memory, RedisVectorMemory)


@pytest.mark.django_db
class TestAgentProcessCommands:
    def test_init_commands_with_default_command_modules(self, task):
        agent_process = AgentProcess(task_id=task.id)
        agent_process.init_commands()
        assert len(agent_process.command_registry.commands) > 0

    def test_init_with_custom_command_modules(self, task, command_output):
        custom_command_modules = ["ix.agents.tests.echo_command"]
        agent_process = AgentProcess(
            task_id=task.id, command_modules=custom_command_modules
        )
        assert agent_process.command_modules == custom_command_modules

    def test_init_commands_invalid_command_module(self, task):
        with pytest.raises(ModuleNotFoundError, match="No module named 'non'"):
            AgentProcess(task_id=task.id, command_modules=["non.existent.CommandClass"])

    def test_commands_execute(self, task, command_output):
        custom_command_modules = ["ix.agents.tests.echo_command"]
        agent_process = AgentProcess(
            task_id=task.id, command_modules=custom_command_modules
        )

        # call command with kwargs
        assert agent_process.execute("echo", output="this is a test")
        command_output.assert_called_once_with("ECHO: this is a test")

        # call command with kwargs
        assert agent_process.execute("noop") is None

    def test_execute_command_not_found(self, task):
        agent_process = AgentProcess(task_id=task.id)
        command_name = "NonExistentCommand"
        kwargs = {"arg1": "value1", "arg2": "value2"}
        with pytest.raises(
            KeyError, match=f"Command '{command_name}' not found in registry."
        ):
            agent_process.execute(command_name, **kwargs)

    def test_commands_execute_with_invalid_args(self, task, command_output):
        custom_command_modules = ["ix.agents.tests.echo_command"]
        agent_process = AgentProcess(
            task_id=task.id, command_modules=custom_command_modules
        )
        with pytest.raises(
            TypeError, match="missing 1 required positional argument: 'name'"
        ):
            agent_process.execute(This="is", invalid="args")


@pytest.mark.django_db
class TestAgentProcessStart:
    def test_start_task(self, task, mock_openai, mock_embeddings):
        """Run task for the first time with no auth to run commands"""
        mock_reply = fake_command_reply(task=task)
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        mock_openai.return_value = msg_to_response(mock_reply)
        return_value = agent_process.start()
        assert return_value is True
        assert query.count() == 4

        think_msg = query[0]
        thought_msg = query[1]
        msg_1 = query[2]
        msg_2 = query[3]

        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"
        assert msg_1.role == "assistant"
        assert msg_1.content["type"] == "COMMAND"
        assert msg_1.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_1.content["command"] == mock_reply.content["command"]
        assert msg_2.role == "assistant"
        assert msg_2.content["type"] == "AUTH_REQUEST"
        assert msg_2.content["message_id"] == str(msg_1.id)

    def test_start_task_with_auth_for_one(
        self, task, mock_openai, command_output, mock_embeddings
    ):
        """Run initial tick + 1 more"""
        mock_reply = fake_command_reply(task=task)
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        mock_openai.return_value = msg_to_response(mock_reply)

        # start process
        # TODO: update testing for initial startup
        return_value = agent_process.start(n=1)
        assert return_value is True

        # first command is authorized
        assert query.count() == 8
        think1_msg = query[0]
        thought1_msg = query[1]
        think2_msg = query[4]
        thought2_msg = query[5]
        assert think1_msg.content["type"] == "THINK"
        assert thought1_msg.content["type"] == "THOUGHT"
        assert think2_msg.content["type"] == "THINK"
        assert thought2_msg.content["type"] == "THOUGHT"

        msg_1 = query[2]
        msg_2 = query[3]
        msg_3 = query[6]
        msg_4 = query[7]
        assert msg_1.role == "assistant"
        assert msg_1.content["type"] == "COMMAND"
        assert msg_1.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_1.content["command"] == mock_reply.content["command"]
        assert msg_2.role == "assistant"
        assert msg_2.content["type"] == "EXECUTED"
        assert msg_2.content["message_id"] == str(msg_1.id)
        command_output.assert_called_once_with("ECHO: this is a test")

        # second command query
        assert msg_3.role == "assistant"
        assert msg_3.content["type"] == "COMMAND"
        assert msg_3.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_3.content["command"] == mock_reply.content["command"]

        # auth required for second command
        assert msg_4.role == "assistant"
        assert msg_4.content["type"] == "AUTH_REQUEST"
        assert msg_4.content["message_id"] == str(msg_3.id)

    def test_start_task_with_auth_for_two(
        self, task, mock_openai, command_output, mock_embeddings
    ):
        """Run initial tick + 2 more"""
        mock_reply = fake_command_reply(task=task)
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        mock_openai.return_value = msg_to_response(mock_reply)

        # start process
        # TODO: update testing for initial startup
        return_value = agent_process.start(n=2)
        assert return_value is True

        # first command is authorized
        assert query.count() == 12
        think1_msg = query[0]
        think2_msg = query[4]
        think3_msg = query[8]
        thought1_msg = query[1]
        thought2_msg = query[5]
        thought3_msg = query[9]
        assert think1_msg.content["type"] == "THINK"
        assert thought1_msg.content["type"] == "THOUGHT"
        assert think2_msg.content["type"] == "THINK"
        assert thought2_msg.content["type"] == "THOUGHT"
        assert think3_msg.content["type"] == "THINK"
        assert thought3_msg.content["type"] == "THOUGHT"

        msg_1 = query[2]
        msg_2 = query[3]
        msg_3 = query[6]
        msg_4 = query[7]
        msg_5 = query[10]
        msg_6 = query[11]
        assert msg_1.role == "assistant"
        assert msg_1.content["type"] == "COMMAND"
        assert msg_1.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_1.content["command"] == mock_reply.content["command"]
        assert msg_2.role == "assistant"
        assert msg_2.content["type"] == "EXECUTED"
        assert msg_2.content["message_id"] == str(msg_1.id)

        # 2nd command query
        assert msg_3.role == "assistant"
        assert msg_3.content["type"] == "COMMAND"
        assert msg_3.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_3.content["command"] == mock_reply.content["command"]
        assert msg_4.role == "assistant"
        assert msg_4.content["type"] == "EXECUTED"
        assert msg_4.content["message_id"] == str(msg_3.id)

        # 3rd command query
        assert msg_5.role == "assistant"
        assert msg_5.content["type"] == "COMMAND"
        assert msg_5.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_5.content["command"] == mock_reply.content["command"]

        # auth required for 3rd command
        assert msg_6.role == "assistant"
        assert msg_6.content["type"] == "AUTH_REQUEST"
        assert msg_6.content["message_id"] == str(msg_5.id)

        # two command calls:
        assert command_output.call_args_list == [
            call("ECHO: this is a test"),
            call("ECHO: this is a test"),
        ]

    def test_restart_task_with_auth_for_none(self, task, mock_openai):
        mock_reply = fake_command_reply(task=task)
        feedback_request = fake_feedback_request(task=task, message_id=mock_reply.id)
        query = TaskLogMessage.objects.filter(
            task=task, created_at__gt=feedback_request.created_at
        )

        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        mock_openai.return_value = msg_to_response(mock_reply)

        # start process
        return_value = agent_process.start()
        assert return_value is True
        assert query.count() == 0

    def test_restart_task_with_auth_for_one(
        self, task, mock_openai, command_output, mock_embeddings
    ):
        mock_reply = fake_command_reply()
        mock_authorization = fake_authorize(message_id=mock_reply.id)
        query = TaskLogMessage.objects.filter(
            task=task, created_at__gt=mock_authorization.created_at
        )
        assert query.count() == 0

        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        mock_openai.return_value = msg_to_response(mock_reply)

        # start process
        return_value = agent_process.start()
        assert return_value is True
        assert query.count() == 5
        think1_msg = query[1]
        thought1_msg = query[2]
        assert think1_msg.content["type"] == "THINK"
        assert thought1_msg.content["type"] == "THOUGHT"

        msg_1 = query[0]
        msg_2 = query[3]
        msg_3 = query[4]

        # first command is authorized
        assert msg_1.role == "assistant"
        assert msg_1.content["type"] == "EXECUTED"
        assert msg_1.content["message_id"] == str(mock_reply.id)
        command_output.assert_called_once_with("ECHO: this is a test")

        # second command
        assert msg_2.role == "assistant"
        assert msg_2.content["type"] == "COMMAND"
        assert msg_2.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_2.content["command"] == mock_reply.content["command"]

        # auth required for second command
        assert msg_3.role == "assistant"
        assert msg_3.content["type"] == "AUTH_REQUEST"
        assert msg_3.content["message_id"] == str(msg_2.id)

    def test_restart_task_with_feedback_and_auth_for_none(
        self, task, mock_openai, mock_embeddings
    ):
        # TODO: test injection of feedback into loop, i.e. is it in context
        mock_reply = fake_command_reply()
        mock_feedback = fake_feedback(task=task, message_id=mock_reply.id)
        query = TaskLogMessage.objects.filter(
            task=task, created_at__gt=mock_feedback.created_at
        )
        assert query.count() == 0

        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        mock_openai.return_value = msg_to_response(mock_reply)

        # start process
        return_value = agent_process.start()
        assert return_value is True
        assert query.count() == 4
        think_msg = query[0]
        thought_msg = query[1]
        msg_1 = query[2]
        msg_2 = query[3]

        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"

        # second command
        assert msg_1.role == "assistant"
        assert msg_1.content["type"] == "COMMAND"
        assert msg_1.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_1.content["command"] == mock_reply.content["command"]

        # auth required for second command
        assert msg_2.role == "assistant"
        assert msg_2.content["type"] == "AUTH_REQUEST"
        assert msg_2.content["message_id"] == str(msg_1.id)

    def test_loop_autonomous(self, task, mock_openai):
        fake_autonomous_toggle(task=task, enabled=1)
        agent_process = AgentProcess(task_id=task.id)
        agent_process.tick = MockTicker(agent_process, task)
        return_value = agent_process.start(n=3)
        assert return_value is False

        # the last item will not be authorized because autonomous mode is disabled
        assert all(agent_process.tick.executes[:-1])
        assert not agent_process.tick.executes[-1]

    def test_loop_exit_on_tick_false(self, task, mock_openai):
        """
        Test that the loop exits when tick returns False. This mechanism allows
        tick to signal to the loop that it should exit even if the loop has not
        yet reached the maximum number of ticks or is in autonomous mode.
        """
        fake_autonomous_toggle(task=task, enabled=1)
        agent_process = AgentProcess(task_id=task.id)
        agent_process.tick = MockTicker(agent_process, task, return_value=False)
        return_value = agent_process.start(n=3)
        assert return_value is False
        # only the first tick should have executed
        assert agent_process.tick.executes == [1]


def msg_to_response(msg: TaskLogMessage):
    """utility for turning model instances back into response json"""
    content = dict(msg.content.items())
    content.pop("type")
    json_content = f"###START###{json.dumps(content)}###END###"
    return {
        "choices": [{"message": {"content": json_content}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 7, "total_tokens": 12},
    }


@pytest.mark.django_db
class TestAgentProcessTicks:
    def test_tick_next_command_no_auth(self, task, mock_openai, mock_embeddings):
        """
        Test ticking for NEXT_COMMAND where the user has not granted
        authentication to execute the command autonomously.

        Should result in agent message for command and auth_request
        """
        mock_reply = fake_command_reply()
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        mock_openai.return_value = msg_to_response(mock_reply)
        agent_process.tick(execute=False)
        assert query.count() == 4
        think_msg = query[0]
        thought_msg = query[1]
        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"

        msg_1 = query[2]
        msg_2 = query[3]
        assert msg_1.role == "assistant"
        assert msg_1.content["type"] == "COMMAND"
        assert msg_1.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_1.content["command"] == mock_reply.content["command"]
        assert msg_2.role == "assistant"
        assert msg_2.content["type"] == "AUTH_REQUEST"
        assert msg_2.content["message_id"] == str(msg_1.id)

    def test_tick_next_command_with_auth(
        self, task, command_output, mock_openai, mock_embeddings
    ):
        """
        Test ticking for NEXT_COMMAND where the user has granted
        authentication to execute the command autonomously.
        """
        mock_reply = fake_command_reply()
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        mock_openai.return_value = msg_to_response(mock_reply)
        agent_process.tick(execute=True)
        assert query.count() == 4
        think_msg = query[0]
        thought_msg = query[1]
        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"
        msg_1 = query[2]
        msg_2 = query[3]

        # command authorized
        assert msg_1.role == "assistant"
        assert msg_1.content["type"] == "COMMAND"
        assert msg_1.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_1.content["command"] == mock_reply.content["command"]
        assert msg_2.role == "assistant"
        assert msg_2.content["type"] == "EXECUTED"
        assert msg_2.content["message_id"] == str(msg_1.id)
        assert msg_2.content["output"] == "echo executed, result=this is a test"
        command_output.assert_called_once_with("ECHO: this is a test")

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
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        mock_openai.return_value = msg_to_response(mock_reply)
        agent_process.tick(user_input="extra input", execute=False)
        assert query.count() == 4

        think_msg = query[0]
        thought_msg = query[1]
        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"

        msg_1 = query[2]
        msg_2 = query[3]
        assert msg_1.role == "assistant"
        assert msg_1.content["type"] == "COMMAND"
        assert msg_1.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_1.content["command"] == mock_reply.content["command"]
        assert msg_2.role == "assistant"
        assert msg_2.content["type"] == "AUTH_REQUEST"
        assert msg_2.content["message_id"] == str(msg_1.id)

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
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        mock_openai.return_value = msg_to_response(mock_reply)
        agent_process.tick(user_input="extra input", execute=True)

        assert query.count() == 4
        think_msg = query[0]
        thought_msg = query[1]
        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"

        msg_1 = query[2]
        msg_2 = query[3]
        assert msg_1.role == "assistant"
        assert msg_1.content["type"] == "COMMAND"
        assert msg_1.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_1.content["command"] == mock_reply.content["command"]
        assert msg_2.role == "assistant"
        assert msg_2.content["type"] == "EXECUTED"
        assert msg_2.content["message_id"] == str(msg_1.id)

        command_output.assert_called_once_with("ECHO: this is a test")

    def test_tick_response_without_command_markers(
        self, task, mock_openai, mock_embeddings
    ):
        mock_reply = fake_command_reply()
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        # Remove command markers from mock reply
        mock_response = msg_to_response(mock_reply)
        mock_content = mock_response["choices"][0]["message"]["content"]
        mock_content = mock_content.replace("###START###", "")
        mock_content = mock_content.replace("###END###", "")
        mock_response["choices"][0]["message"]["content"] = mock_content
        mock_openai.return_value = mock_response
        return_value = agent_process.tick(execute=True)

        # return value is True because the loop should continue
        assert return_value is True

        assert query.count() == 3
        think_msg = query[0]
        thought_msg = query[1]
        msg_1 = query[2]

        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"
        assert msg_1.role == "system"
        assert msg_1.content["type"] == "EXECUTE_ERROR"
        assert msg_1.content == {
            "text": "",
            "type": "EXECUTE_ERROR",
            "error_type": "MissingCommandMarkers",
            "message_id": "None",
        }

    def test_tick_response_with_question(self, task, mock_openai, mock_embeddings):
        """Test that question response are parsed as expected"""
        mock_reply = fake_feedback_request(task=task)
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        mock_openai.return_value = msg_to_response(mock_reply)
        return_value = agent_process.tick(execute=True)

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

    def test_tick_command_not_in_response(self, task, mock_openai, mock_embeddings):
        mock_reply = fake_command_reply()
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        del mock_reply.content["command"]
        mock_openai.return_value = msg_to_response(mock_reply)
        return_value = agent_process.tick(execute=True)

        # return value is True because the loop should continue
        assert return_value is True

        assert query.count() == 4
        think_msg = query[0]
        thought_msg = query[1]
        msg_1 = query[2]
        msg_2 = query[3]

        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"
        assert msg_1.role == "assistant"
        assert msg_1.content["type"] == "COMMAND"
        assert msg_1.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_2.role == "system"
        assert msg_2.content["type"] == "EXECUTE_ERROR"
        assert msg_2.content == {
            "text": "respond in the expected format",
            "type": "EXECUTE_ERROR",
            "error_type": "missing command",
            "message_id": str(msg_1.id),
        }

    def test_tick_command_name_not_in_response(
        self, task, mock_openai, mock_embeddings
    ):
        mock_reply = fake_command_reply()
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        mock_reply.content["command"] = {"args": []}
        mock_openai.return_value = msg_to_response(mock_reply)
        return_value = agent_process.tick(execute=True)

        # return value is True because the loop should continue
        assert return_value is True

        assert query.count() == 4
        think_msg = query[0]
        thought_msg = query[1]
        msg_1 = query[2]
        msg_2 = query[3]

        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"
        assert msg_1.role == "assistant"
        assert msg_1.content["type"] == "COMMAND"
        assert msg_1.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_1.content["command"] == mock_reply.content["command"]
        assert msg_2.role == "system"
        assert msg_2.content["type"] == "EXECUTE_ERROR"
        assert msg_2.content == {
            "text": "respond in the expected format",
            "type": "EXECUTE_ERROR",
            "error_type": "missing command",
            "message_id": str(msg_1.id),
        }

    def test_tick_command_args_not_in_response(
        self, task, mock_openai, mock_embeddings
    ):
        mock_reply = fake_command_reply()
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        mock_reply.content["command"] = {"name": "echo"}
        mock_openai.return_value = msg_to_response(mock_reply)
        return_value = agent_process.tick(execute=True)

        # return value is True because the loop should continue
        assert return_value is True

        assert query.count() == 4
        think_msg = query[0]
        thought_msg = query[1]
        msg_1 = query[2]
        msg_2 = query[3]

        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"
        assert msg_1.role == "assistant"
        assert msg_1.content["type"] == "COMMAND"
        assert msg_1.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_1.content["command"] == mock_reply.content["command"]
        assert msg_2.role == "system"
        assert msg_2.content["type"] == "EXECUTE_ERROR"
        assert msg_2.content == {
            "text": "respond in the expected format",
            "type": "EXECUTE_ERROR",
            "error_type": "missing command",
            "message_id": str(msg_1.id),
        }

    def test_tick_unknown_command_in_response(self, task, mock_openai, mock_embeddings):
        mock_reply = fake_command_reply()
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        mock_reply.content["command"] = {"name": "does_not_exist", "args": []}
        mock_openai.return_value = msg_to_response(mock_reply)
        return_value = agent_process.tick(execute=True)

        # return value is True because the loop should continue
        assert return_value is True

        assert query.count() == 4
        think_msg = query[0]
        thought_msg = query[1]
        msg_1 = query[2]
        msg_2 = query[3]

        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"
        assert msg_1.role == "assistant"
        assert msg_1.content["type"] == "COMMAND"
        assert msg_1.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_1.content["command"] == mock_reply.content["command"]
        assert msg_2.role == "system"
        assert msg_2.content["type"] == "EXECUTE_ERROR"
        assert msg_2.content == {
            "text": "does_not_exist is not available",
            "type": "EXECUTE_ERROR",
            "error_type": "unknown command",
            "message_id": str(msg_1.id),
        }

    def test_tick_command_failure(self, task, mock_openai, mock_embeddings):
        mock_reply = fake_command_reply()
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        mock_reply.content["command"] = {"name": "fail", "args": {}}
        mock_openai.return_value = msg_to_response(mock_reply)
        return_value = agent_process.tick(execute=True)

        # return value is True because the loop should continue
        assert return_value is True

        assert query.count() == 4
        think_msg = query[0]
        thought_msg = query[1]
        msg_1 = query[2]
        msg_2 = query[3]

        assert think_msg.content["type"] == "THINK"
        assert thought_msg.content["type"] == "THOUGHT"
        assert msg_1.role == "assistant"
        assert msg_1.content["type"] == "COMMAND"
        assert msg_1.content["thoughts"] == mock_reply.content["thoughts"]
        assert msg_1.content["command"] == mock_reply.content["command"]
        assert msg_2.role == "system"
        assert msg_2.content["type"] == "EXECUTE_ERROR"
        assert msg_2.content == {
            "text": "This is a test failure",
            "type": "EXECUTE_ERROR",
            "error_type": "Exception",
            "message_id": str(msg_1.id),
        }


@pytest.mark.django_db
class TestAgentProcessAIChat:
    def test_chat_with_ai(self, task, mock_openai, mock_embeddings):
        mock_reply = fake_command_reply()
        mock_reply.delete()
        query = TaskLogMessage.objects.filter(task=task)
        assert query.count() == 0

        mock_openai.return_value = msg_to_response(mock_reply)
        agent_process = AgentProcess(task_id=task.id)
        message = "Test message"
        agent_process.chat_with_ai(message)
        mock_openai.assert_called()

        assert query.count() == 2
        think_msg = query[0]
        thought_msg = query[1]
        assert think_msg.content["type"] == "THINK"
        assert think_msg.content["input"] == "Test message"
        assert thought_msg.content["type"] == "THOUGHT"
        assert isinstance(thought_msg.content["runtime"], float)
        assert thought_msg.content["usage"] == {
            "completion_tokens": 7,
            "prompt_tokens": 5,
            "total_tokens": 12,
        }


@pytest.mark.django_db
class TestAgentProcessPrompt:
    def test_construct_prompt_for_task_with_goals(self, task):
        task.goals = [
            {"description": "Goal 0", "task": "GOAL"},
            {"description": "Goal 1", "type": "GOAL"},
            {"description": "Goal 2", "type": "GOAL"},
        ]
        task.save()
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        prompt = agent_process.construct_base_prompt()
        # just sanity checks for now
        assert prompt is not None

    def test_construct_prompt_for_task_without_goals(self, task):
        task.goals = []
        task.save()
        agent_process = AgentProcess(
            task_id=task.id, command_modules=["ix.agents.tests.echo_command"]
        )
        prompt = agent_process.construct_base_prompt()
        # just sanity checks for now
        assert prompt is not None
