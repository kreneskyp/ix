import logging
from copy import deepcopy
from typing import Optional, Any

from langchain.schema.runnable import Runnable, RunnableConfig
from langchain.schema.runnable.utils import Output
from pydantic.v1 import BaseModel as BaseModelV1

logger = logging.getLogger(__name__)


MOCK_RUNNABLE_CLASS_PATH = "ix.chains.tests.mock_runnable.MockRunnable"
MOCK_RUNNABLE_CONFIG = {
    "name": "mock_runnable",
    "description": "mock runnable for testing",
    "class_path": MOCK_RUNNABLE_CLASS_PATH,
    "type": "chain",
    "config": {},
}


class MockRunnableInput(BaseModelV1):
    value: str = "input"


class MockRunnable(Runnable[MockRunnableInput, Output], BaseModelV1):
    """Mock runnable that returns a default value"""

    name: str = "default"
    value: Any = "output"

    def invoke(
        self,
        input: MockRunnableInput,
        config: Optional[RunnableConfig] = None,
    ) -> dict:
        if isinstance(input, dict):
            output = deepcopy(input)
            output[self.name] = self.value
            return output

        return {
            "input": input,
            self.name: self.value,
        }
