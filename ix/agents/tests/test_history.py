import pytest

from ix.agents.history import TaskHistory
from ix.agents.tests.test_process import MessageTeardown
from ix.task_log.models import TaskLogMessage
from ix.task_log.tests.fake import (
    fake_task_log_msg,
    fake_autonomous_toggle,
    fake_command_reply,
    fake_task_log_msg_type,
)


@pytest.mark.django_db
class TestAgentProcessHistory(MessageTeardown):
    MSG_1 = {"type": "COMMAND", "message": "THIS IS A TEST 1"}
    MSG_2 = {"type": "COMMAND", "message": "THIS IS A TEST 2"}
    MSG_3 = {"type": "COMMAND", "message": "THIS IS A TEST 3"}
    MSG_4 = {"type": "COMMAND", "message": "THIS IS A TEST 4"}

    @pytest.mark.parametrize("content_type", TaskHistory.EXCLUDED_MSG_TYPES)
    def test_query_message_excludes_msgs(self, content_type, task):
        """Test that non-relevant messages are excluded from history"""
        msg = fake_task_log_msg_type(content_type, task=task)
        agent_process = TaskHistory(task_id=task.id)
        agent_process.update_message_history()

        for history_msg in agent_process.history:
            assert history_msg != msg.as_message()

    @pytest.mark.parametrize(
        "content_type", ["FEEDBACK", "COMMAND", "EXECUTED", "EXECUTE_ERROR"]
    )
    def test_query_message_includes_types(self, content_type, task):
        """Test that relevant messages are included in history"""
        msg = fake_task_log_msg_type(content_type, task=task)
        agent_process = TaskHistory(task_id=task.id)
        agent_process.update_message_history()
        assert len(agent_process.history) >= 1
        assert agent_process.history[-1] == msg.as_message()

    def test_query_message_history_without_since(self, task):
        """Test querying all messages"""
        msg1 = fake_task_log_msg(task=task)
        msg2 = fake_task_log_msg(task=task)
        agent_process = TaskHistory(task_id=task.id)
        messages = agent_process.query_message_history()
        assert messages.count() == 2
        assert messages.filter(id=msg1.id).exists()
        assert messages.filter(id=msg2.id).exists()

    def test_query_message_history_with_since(self, task):
        """Test querying new messages"""
        msg1 = fake_task_log_msg(task=task)
        msg2 = fake_task_log_msg(task=task)
        agent_process = TaskHistory(task_id=task.id)
        messages = agent_process.query_message_history(since=msg1.created_at)
        assert messages.count() == 1
        assert not messages.filter(id=msg1.id).exists()
        assert messages.filter(id=msg2.id).exists()

    def test_update_message_history_no_messages(self, task):
        """initializing history before there are messages"""
        agent_process = TaskHistory(task_id=task.id)
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
        agent_process = TaskHistory(task_id=task.id)
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
        agent_process = TaskHistory(task_id=task.id)
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
        agent_process = TaskHistory(task_id=task.id)
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
        agent_process = TaskHistory(task_id=task.id)
        agent_process.update_message_history()
        assert not agent_process.autonomous

        fake_task_log_msg(task=task, content=self.MSG_1)
        fake_autonomous_toggle(enabled=1)
        fake_autonomous_toggle(enabled=0)
        fake_autonomous_toggle(enabled=1)
        fake_task_log_msg(task=task, content=self.MSG_1)
        agent_process.update_message_history()
        assert agent_process.autonomous
