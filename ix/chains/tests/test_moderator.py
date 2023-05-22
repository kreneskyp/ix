from uuid import UUID

import pytest
from ix.agents.callback_manager import IxCallbackManager
from ix.chains.llm_chain import LLMChain
from ix.chains.moderator import ChatModerator


@pytest.mark.django_db
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
        mock_openai.return_value = '{"agent": "agent_1"}'

        chat_moderator = chat["instance"]
        result = chat_moderator._call(
            {"user_input": "say hello to agent 1", "chat_id": str(chat["chat"].id)}
        )

        assert "task_id" in result
        assert UUID(result["task_id"])

    def test_from_config(self, chat):
        """Test that the ChatModerator is created with the correct dependencies from config"""
        callback_manager = IxCallbackManager(chat["chat"].task)
        config = {
            "llm": {
                "class_path": "langchain.chat_models.openai.ChatOpenAI",
                "config": {"request_timeout": 60, "temperature": 0.2, "verbose": True},
            }
        }

        chat_moderator = ChatModerator.from_config(config, callback_manager)

        assert isinstance(chat_moderator.selection_chain, LLMChain)
        assert chat_moderator.callback_manager == callback_manager
