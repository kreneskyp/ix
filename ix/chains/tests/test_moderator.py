import pytest


@pytest.mark.django_db
class TestChatModerator:
    def test_agent_prompt(self, chat):
        """Test that the agent prompt is formatted correctly"""

        ix_node = chat["instance"]
        chat_moderator = ix_node.child
        agent_prompt = chat_moderator.agent_prompt(chat["chat"])

        assert (
            agent_prompt
            == """0. agent_1: to test selections\n1. agent_2: to test selections"""
        )

    async def test_acall(self, mock_openai, achat, mocker, aix_handler):
        # mock start_agent_loop since the task is async and makes this test flaky
        mocker.patch("ix.chains.moderator.start_agent_loop")

        mock_openai.return_value = dict(
            name="delegate_to_agent", arguments={"agent_id": 1}
        )

        ix_node = achat["instance"]
        chat_moderator = ix_node.child

        result = await chat_moderator.acall(
            {"user_input": "say hello to agent 1", "chat_id": str(achat["chat"].id)},
            callbacks=[aix_handler],
        )

        assert result["text"] == "Delegating to @agent_2"
        assert "chat_history" in result
