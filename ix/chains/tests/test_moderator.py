import pytest


@pytest.mark.django_db
@pytest.mark.usefixtures("node_types")
class TestChatModerator:
    def test_agent_prompt(self, chat):
        """Test that the agent prompt is formatted correctly"""

        chat_moderator = chat["instance"]
        agent_prompt = chat_moderator.agent_prompt(chat["chat"])

        assert (
            agent_prompt
            == """0. agent_1: to test selections\n1. agent_2: to test selections"""
        )

    def test_call(self, mock_openai, chat):
        mock_openai.return_value = dict(
            name="delegate_to_agent", arguments={"agent_id": 1}
        )

        chat_moderator = chat["instance"]
        result = chat_moderator(
            {"user_input": "say hello to agent 1", "chat_id": str(chat["chat"].id)}
        )

        assert result["text"] == "Delegating to @agent_2"
        assert "chat_history" in result
