from typing import Dict, Any, List

from langchain.schema import BaseMemory


class VocabularyMemory(BaseMemory):
    @property
    def memory_variables(self) -> List[str]:
        pass

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        pass

    def clear(self) -> None:
        pass
