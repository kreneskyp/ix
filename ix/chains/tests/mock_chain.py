import logging
from typing import Dict, List, Any

from langchain.chains.base import Chain

from ix.agents.callback_manager import IxCallbackManager

logger = logging.getLogger(__name__)


def mock_chain_func(inputs: Dict[str, str]) -> Dict[str, str]:
    """Mock chain function that just returns the input"""
    chain_input = inputs["mock_chain_input"]
    result = {"mock_chain_output": chain_input}
    logger.debug(f"MockChain.call input={chain_input}")
    logger.debug(f"MockChain.call result={result}")
    return result


MOCK_CHAIN_CONFIG = {
    "name": "mock_chain",
    "description": "mock chain for testing",
    "class_path": "ix.chains.tests.mock_chain.MockChain",
    "config": {},
}


class MockChain(Chain):
    """
    Mock chain for testing. It just returns the input as output
    """

    @property
    def _chain_type(self) -> str:
        return "ix_test"

    @property
    def input_keys(self) -> List[str]:
        return ["mock_chain_input"]

    @property
    def output_keys(self) -> List[str]:
        return ["mock_chain_output"]

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        return mock_chain_func(inputs)

    async def _acall(self, inputs: Dict[str, str]) -> Dict[str, str]:
        return mock_chain_func(inputs)

    @classmethod
    def from_config(
        cls, config: Dict[str, Any], callback_manager: IxCallbackManager
    ) -> "MockChain":
        chain = MockChain(**config)
        chain.callbacks = callback_manager
        return chain
