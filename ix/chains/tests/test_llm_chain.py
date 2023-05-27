import pytest
from unittest.mock import MagicMock
from langchain.chat_models.openai import ChatOpenAI

from ix.agents.callback_manager import IxCallbackManager
from ix.chains.llm_chain import LLMChain, TEMPLATE_CLASSES
from ix.chains.tests.mock_memory import MockMemory

EXAMPLE_CONFIG = {
    "class_path": "ix.chains.tool_chain.LLMToolChain",
    "config": {
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
            "config": {"request_timeout": 120, "temperature": 0.2, "verbose": True},
        },
        "memory": {
            "class_path": "ix.chains.tests.mock_memory.MockMemory",
            "config": {"value_map": {'mock_memory_input': 'mock memory'}},
        },
        "messages": [
            {
                "role": "system",
                "template": "Say hello to {name} and answer user question",
                "partial_variables": {
                    "name": "test user",
                },
            },
            {
                "role": "user",
                "template": "Question: {user_input}",
                "input_variables": ["user_input"],
            },
            {"role": "assistant", "template": "Answer: ANSWER"},
        ],
    },
}


@pytest.fixture
def callback_manager_mock(mocker):
    return mocker.MagicMock(spec=IxCallbackManager)


@pytest.fixture
def load_llm_mock(mocker):
    return mocker.patch(
        "ix.chains.llm_chain.load_llm", return_value=MagicMock(spec=ChatOpenAI)
    )


class TestLLMChain:
    @pytest.mark.parametrize("role", [role for role in TEMPLATE_CLASSES.keys()])
    def test_create_message(self, role):
        message = {
            "role": role,
            "template": "hello {name} i will answer {user_input}",
            "input_variables": ["user_input"],
            "partial_variables": {"name": "test user"},
        }
        config = {"config_key": "config_value"}
        context = {"context_key": "context_value"}

        result = LLMChain.create_message(message, config, context)

        assert isinstance(result, TEMPLATE_CLASSES[role])
        assert result.prompt.partial_variables == {"name": "test user"}

    def test_prepare_config(self, load_llm_mock, callback_manager_mock):
        config = EXAMPLE_CONFIG["config"].copy()

        prepared_config, context = LLMChain.prepare_config(
            config, callback_manager_mock
        )

        assert prepared_config["llm"] == load_llm_mock.return_value
        assert context == {}

    def test_from_config(self, load_llm_mock, callback_manager_mock):
        config = EXAMPLE_CONFIG["config"].copy()
        chain = LLMChain.from_config(config, callback_manager_mock)

        assert isinstance(chain, LLMChain)
        assert (
            chain.prompt.messages[0].prompt.partial_variables
            == EXAMPLE_CONFIG["config"]["messages"][0]["partial_variables"]
        )
        assert chain.prompt.messages[1].prompt.partial_variables == {}
        assert chain.callbacks == callback_manager_mock

        assert isinstance(chain.memory, MockMemory)
