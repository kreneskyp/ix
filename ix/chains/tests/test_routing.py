import logging
from copy import deepcopy
from unittest.mock import MagicMock

import pytest
from langchain.schema import HumanMessage

from ix.chains.models import ChainNode
from ix.chains.routing import MapSubchain
from ix.chains.tests.mock_chain import MOCK_CHAIN_CONFIG
from ix.chains.tests.test_config_loader import (
    LLM_REPLY_WITH_HISTORY,
    LLM_REPLY_WITH_HISTORY_AND_MEMORY,
    LLM_REPLY,
)
from ix.task_log.tests.fake import fake_chain

logger = logging.getLogger(__name__)


MAP_SUBCHAIN = {
    "name": "refine",
    "description": "testing MapSubchain",
    "class_path": "ix.chains.routing.MapSubchain",
    "config": {
        "input_variables": ["input1"],
        "map_input": "input1",
        "map_input_to": "mock_chain_input",
        "output_key": "output1",
        "chains": [MOCK_CHAIN_CONFIG],
    },
}


MAP_SUBCHAIN_WITH_MEMORY = {
    "name": "refine",
    "description": "testing MapSubchain",
    "class_path": "ix.chains.routing.MapSubchain",
    "config": {
        "input_variables": ["user_inputs"],
        "map_input": "user_inputs",
        "map_input_to": "user_input",
        "output_key": "output1",
        "memory": [
            {
                "class_path": "ix.chains.tests.mock_memory.MockMemory",
                "config": {},
            }
        ],
        "chains": [LLM_REPLY_WITH_HISTORY],
    },
}


EMPTY_SEQUENCE = {
    "name": "test sequence",
    "description": "testing SequentialChain",
    "class_path": "langchain.chains.SequentialChain",
    "config": {
        "input_variables": ["user_input"],
    },
}

SEQUENCE = {
    "name": "test sequence",
    "description": "testing SequentialChain",
    "class_path": "langchain.chains.SequentialChain",
    "config": {
        "input_variables": ["user_input"],
        "chains": [LLM_REPLY],
    },
}

# memory configured on sequence
SEQUENCE_WITH_MEMORY = {
    "class_path": "langchain.chains.SequentialChain",
    "config": {
        "chains": [LLM_REPLY_WITH_HISTORY],
        "memory": [
            {
                "class_path": "ix.chains.tests.mock_memory.MockMemory",
                "config": {},
            }
        ],
        "input_variables": ["user_input"],
    },
}

SEQUENCE_WITH_LLM_WITH_MEMORY = {
    "name": "test sequence",
    "description": "testing SequentialChain",
    "class_path": "langchain.chains.SequentialChain",
    "config": {
        "input_variables": ["user_input"],
        "chains": [LLM_REPLY_WITH_HISTORY_AND_MEMORY],
    },
}


@pytest.fixture
def mock_subchain_config():
    config = deepcopy(MAP_SUBCHAIN)
    config["config"]["chains"] = [MOCK_CHAIN_CONFIG]
    yield config


@pytest.mark.django_db
class TestSequentialChain:
    """Test loading sequences"""

    def test_load(self, load_chain, mock_openai):
        mock_openai.__dict__["completion_with_retry"] = MagicMock(
            return_value=mock_openai.get_mock_content()
        )

        # create chain
        chain = load_chain(SEQUENCE)

        # verify result
        result = chain.run(user_input="test1")
        assert result == "mock llm response"

    def test_with_memory(self, load_chain, mock_openai):
        mock_openai.__dict__["completion_with_retry"] = MagicMock(
            return_value=mock_openai.get_mock_content()
        )

        # create chain
        chain = load_chain(SEQUENCE_WITH_MEMORY)

        # verify result
        result = chain.run(user_input="test1")
        assert result == "mock llm response"
        messages = mock_openai.completion_with_retry.call_args_list[0].kwargs[
            "messages"
        ]
        system_message = messages[0]
        assert system_message["content"] == "You are a test bot! HISTORY: mock memory"

    def test_with_memory_on_chain(self, load_chain, mock_openai):
        mock_openai.__dict__["completion_with_retry"] = MagicMock(
            return_value=mock_openai.get_mock_content()
        )

        # create chain
        chain = load_chain(SEQUENCE_WITH_LLM_WITH_MEMORY)

        # pre-seed memory
        chain.chains[0].memory.chat_memory.messages = [
            HumanMessage(content="this is a seeded memory")
        ]

        # verify result
        result = chain.run(user_input="test1")
        assert result == "mock llm response"
        messages = mock_openai.completion_with_retry.call_args_list[0].kwargs[
            "messages"
        ]
        system_message = messages[0]
        assert (
            system_message["content"]
            == "You are a test bot! HISTORY: Human: this is a seeded memory"
        )


@pytest.fixture()
def mock_mapsubchain(load_chain) -> MapSubchain:
    yield load_chain(MAP_SUBCHAIN)


@pytest.mark.django_db
class TestMapSubchain:
    def test_from_config(self, node_types, mock_subchain_config, ix_context):
        """Testing importing from a config object"""
        chain = fake_chain()
        chain_node = ChainNode.objects.create_from_config(
            chain, mock_subchain_config, root=True
        )
        instance = chain_node.load(ix_context)
        assert isinstance(instance, MapSubchain)

    def test_load_chain(self, mock_mapsubchain):
        assert isinstance(mock_mapsubchain, MapSubchain)

    def test_call(self, mock_mapsubchain):
        chain = mock_mapsubchain
        inputs = {"input1": ["test1", "test2", "test3"]}
        output = chain.run(**inputs)
        assert output == ["test1", "test2", "test3"]

    def test_call_nested_input_map(self, mock_subchain_config, load_chain, mock_openai):
        # setup nested map_input
        config = mock_subchain_config["config"]
        config["map_input"] = "input1.level2"
        chain = load_chain(mock_subchain_config)

        # run test
        inputs = {"input1": {"level2": ["test1", "test2", "test3"]}}
        output = chain.run(**inputs)
        assert output == ["test1", "test2", "test3"]

    async def test_acall(self, mock_mapsubchain):
        chain = mock_mapsubchain
        inputs = {"input1": ["test1", "test2", "test3"]}
        output = await chain.arun(**inputs)
        assert output == ["test1", "test2", "test3"]

    async def test_acall_nested_input_map(
        self, mock_subchain_config, aload_chain, mock_openai
    ):
        # setup nested map_input
        config = mock_subchain_config["config"]
        config["map_input"] = "input1.level2"
        chain = await aload_chain(mock_subchain_config)

        # run test
        inputs = {"input1": {"level2": ["test1", "test2", "test3"]}}
        output = await chain.arun(**inputs)
        assert output == ["test1", "test2", "test3"]

    def test_memory(self, load_chain, mock_openai):
        mock_openai.__dict__["completion_with_retry"] = MagicMock(
            return_value=mock_openai.get_mock_content()
        )

        # create chain
        chain = load_chain(MAP_SUBCHAIN_WITH_MEMORY)

        # run chain
        inputs = {"user_inputs": ["test1", "test2", "test3"]}
        output = chain.run(**inputs)
        assert output == ["mock llm response", "mock llm response", "mock llm response"]

        # assert memory was in the prompts
        call_args_list = mock_openai.completion_with_retry.call_args_list
        assert len(call_args_list) == 3
        system_message1 = call_args_list[0].kwargs["messages"][0]["content"]
        system_message2 = call_args_list[1].kwargs["messages"][0]["content"]
        system_message3 = call_args_list[2].kwargs["messages"][0]["content"]
        assert "HISTORY: mock memory" in system_message1

        # memories are only saved at the end of the chain since memory is added to the sequence
        assert "Human: test1" not in system_message2
        assert "Human: test1" not in system_message3
        assert "Human: test2" not in system_message3
