from copy import deepcopy
from unittest.mock import MagicMock

import pytest
from langchain.schema import HumanMessage

from ix.agents.llm import load_chain
from ix.chains.models import ChainNode
from ix.chains.routing import MapSubchain
from ix.chains.tests.mock_chain import MOCK_CHAIN_CONFIG
from ix.chains.tests.test_config_loader import (
    MEMORY,
    LLM_REPLY_WITH_HISTORY,
    LLM_REPLY_WITH_HISTORY_AND_MEMORY,
    LLM_REPLY,
)

MAP_SUBCHAIN = {
    "name": "refine",
    "node_type": "list",
    "description": "testing MapSubchain",
    "class_path": "ix.chains.routing.MapSubchain",
    "config": {
        "input_variables": ["input1"],
        "map_input": "input1",
        "map_input_to": "mock_chain_input",
        "output_key": "output1",
    },
}


MAP_SUBCHAIN_WITH_MEMORY = {
    "name": "refine",
    "node_type": "list",
    "description": "testing MapSubchain",
    "class_path": "ix.chains.routing.MapSubchain",
    "config": {
        "input_variables": ["user_inputs"],
        "map_input": "user_inputs",
        "map_input_to": "user_input",
        "output_key": "output1",
        "memory": MEMORY,
    },
}


SEQUENCE = {
    "name": "test sequence",
    "node_type": "list",
    "description": "testing IXSequence",
    "class_path": "ix.chains.routing.IXSequence",
    "config": {
        "input_variables": ["user_input"],
    },
}


# memory configured on sequence
SEQUENCE_WITH_MEMORY = {
    "class_path": "ix.chains.routing.IXSequence",
    "node_type": "list",
    "config": {
        "chains": [],
        "memory": MEMORY,
        "input_variables": ["user_input"],
    },
}


@pytest.fixture
def mock_subchain_config():
    config = deepcopy(MAP_SUBCHAIN)
    config["config"]["chains"] = [MOCK_CHAIN_CONFIG]
    yield config


@pytest.mark.django_db
class TestIXSequence:
    """Test loading sequences"""

    def test_load(self, mock_callback_manager, mock_openai):
        mock_openai.__dict__["completion_with_retry"] = MagicMock(
            return_value=mock_openai.get_mock_content()
        )

        # create chain
        node = ChainNode.objects.create(**SEQUENCE)
        node.add_child(**LLM_REPLY)
        chain = node.load_chain(mock_callback_manager)

        # verify result
        result = chain.run(user_input="test1")
        assert result == "mock llm response"

    def test_load_without_chains(self, mock_callback_manager):
        """Requires at least one child chain"""
        node = ChainNode.objects.create(**SEQUENCE)
        with pytest.raises(ValueError, match="IXSequence requires at least one chain"):
            node.load_chain(mock_callback_manager)

    def test_with_memory(self, mock_callback_manager, mock_openai):
        mock_openai.__dict__["completion_with_retry"] = MagicMock(
            return_value=mock_openai.get_mock_content()
        )

        # create chain
        node = ChainNode.objects.create(**SEQUENCE_WITH_MEMORY)
        node.add_child(**LLM_REPLY_WITH_HISTORY)
        chain = node.load_chain(mock_callback_manager)

        # pre-seed memory
        chain.memory.chat_memory.messages = [
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

    def test_with_memory_on_chain(self, mock_callback_manager, mock_openai):
        mock_openai.__dict__["completion_with_retry"] = MagicMock(
            return_value=mock_openai.get_mock_content()
        )

        # create chain
        node = ChainNode.objects.create(**SEQUENCE)
        node.add_child(**LLM_REPLY_WITH_HISTORY_AND_MEMORY)
        chain = node.load_chain(mock_callback_manager)

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


@pytest.mark.django_db
class TestMapSubchain:
    def test_from_config(self, mock_subchain_config, mock_callback_manager):
        chain = MapSubchain.from_config(
            mock_subchain_config["config"], callback_manager=mock_callback_manager
        )
        assert isinstance(chain, MapSubchain)

    def test_load_chain(self, mock_subchain_config, mock_callback_manager):
        chain = load_chain(mock_subchain_config, callback_manager=mock_callback_manager)
        assert isinstance(chain, MapSubchain)

    def test_call(self, mock_subchain_config, mock_callback_manager):
        chain = MapSubchain.from_config(
            mock_subchain_config["config"], callback_manager=mock_callback_manager
        )
        inputs = {"input1": ["test1", "test2", "test3"]}
        output = chain.run(**inputs)
        assert output == ["test1", "test2", "test3"]

    def test_call_nested_input_map(self, mock_subchain_config, mock_callback_manager):
        # setup nested map_input
        config = mock_subchain_config["config"]
        config["map_input"] = "input1.level2"

        # run test
        chain = MapSubchain.from_config(config, callback_manager=mock_callback_manager)
        inputs = {"input1": {"level2": ["test1", "test2", "test3"]}}
        output = chain.run(**inputs)
        assert output == ["test1", "test2", "test3"]

    def test_model_save_load_run(self, mock_callback_manager):
        # create nodes
        node = ChainNode.objects.create(**MAP_SUBCHAIN)
        node.add_child(**MOCK_CHAIN_CONFIG)

        # load chain
        chain = node.load_chain(mock_callback_manager)

        # run chain
        inputs = {"input1": ["test1", "test2", "test3"]}
        output = chain.run(**inputs)
        assert output == ["test1", "test2", "test3"]

    def test_memory(self, mock_callback_manager, mock_openai):
        mock_openai.__dict__["completion_with_retry"] = MagicMock(
            return_value=mock_openai.get_mock_content()
        )

        # create chain
        node = ChainNode.objects.create(**MAP_SUBCHAIN_WITH_MEMORY)
        node.add_child(**LLM_REPLY_WITH_HISTORY)
        chain = node.load_chain(mock_callback_manager)

        # pre-seed memory (chain is on MapSubchains internal IXSequence)
        chain.chain.memory.chat_memory.messages = [
            HumanMessage(content="this is a seeded memory")
        ]

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
        assert "this is a seeded memory" in system_message1
        assert "Human: test1" in system_message2
        assert "Human: test1" in system_message3
        assert "Human: test2" in system_message3
