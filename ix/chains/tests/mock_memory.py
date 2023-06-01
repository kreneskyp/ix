from typing import Dict, Any, List

from langchain.schema import BaseMemory


class MockMemory(BaseMemory):
    """
    Mock memory that returns a fixed set of values
    Used for testing only.
    """

    value_map: Dict[str, str] = {"mock_memory_input": "mock memory"}
    session_id: str = "mock_session_id"

    @property
    def memory_variables(self) -> List[str]:
        return list(self.value_map.keys())

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return self.value_map

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        pass

    def clear(self) -> None:
        pass
