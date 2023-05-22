from copy import deepcopy

import pytest

from ix.agents.llm import load_chain
from ix.chains.models import ChainNode
from ix.chains.routing import MapSubchain
from ix.chains.tests.mock_chain import MOCK_CHAIN_CONFIG

EXAMPLE_CONFIG = {
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


@pytest.fixture
def mock_subchain_config():
    config = deepcopy(EXAMPLE_CONFIG)
    config["config"]["chains"] = [MOCK_CHAIN_CONFIG]
    yield config


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
        node = ChainNode.objects.create(**EXAMPLE_CONFIG)
        node.add_child(**MOCK_CHAIN_CONFIG)

        # load chain
        chain = node.load_chain(mock_callback_manager)

        # run chain
        inputs = {"input1": ["test1", "test2", "test3"]}
        output = chain.run(**inputs)
        assert output == ["test1", "test2", "test3"]
