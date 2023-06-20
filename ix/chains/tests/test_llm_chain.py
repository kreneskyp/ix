from copy import deepcopy

import pytest
from langchain.prompts import ChatPromptTemplate

from ix.agents.callback_manager import IxCallbackManager
from ix.chains.llm_chain import LLMChain, TEMPLATE_CLASSES
from ix.chains.loaders.prompts import create_message
from ix.chains.tests.mock_memory import MockMemory
from ix.chains.tests.test_config_loader import OPENAI_LLM, MOCK_MEMORY

PROMPT_TEMPLATE = {
    "class_path": "langchain.prompts.chat.ChatPromptTemplate",
    "config": {
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


EXAMPLE_CONFIG = {
    "class_path": "ix.chains.tool_chain.LLMToolChain",
    "config": {
        "llm": OPENAI_LLM,
        "memory": MOCK_MEMORY,
        "prompt": PROMPT_TEMPLATE,
    },
}


@pytest.mark.django_db
class TestChatPromptTemplate:
    def test_create_message(self):
        message = {
            "role": "user",
            "template": "hello {name} i will answer {user_input}",
            "input_variables": ["user_input"],
            "partial_variables": {"name": "test user"},
        }

        # TODO: context
        config = {"config_key": "config_value"}
        context = {"context_key": "context_value"}

        result = create_message(message)

        assert isinstance(result, TEMPLATE_CLASSES["user"])
        assert result.prompt.partial_variables == {"name": "test user"}

    def test_from_config(self, load_chain):
        config = deepcopy(PROMPT_TEMPLATE)
        chain = load_chain(config)
        assert isinstance(chain, ChatPromptTemplate)
        assert len(chain.messages) == 3
        assert isinstance(chain.messages[0], TEMPLATE_CLASSES["system"])
        assert isinstance(chain.messages[1], TEMPLATE_CLASSES["user"])
        assert isinstance(chain.messages[2], TEMPLATE_CLASSES["assistant"])


@pytest.mark.django_db
class TestLLMChain:
    def test_from_config(self, load_chain):
        config = deepcopy(EXAMPLE_CONFIG)
        chain = load_chain(config)

        assert isinstance(chain, LLMChain)
        assert (
            chain.prompt.messages[0].prompt.partial_variables
            == EXAMPLE_CONFIG["config"]["prompt"]["config"]["messages"][0][
                "partial_variables"
            ]
        )
        assert chain.prompt.messages[1].prompt.partial_variables == {}
        assert isinstance(chain.callbacks, IxCallbackManager)
        assert isinstance(chain.memory, MockMemory)
