import logging
from copy import deepcopy
from typing import Optional, Any

from langchain.schema.runnable import Runnable, RunnableConfig
from langchain.schema.runnable.utils import Output
from pydantic.v1 import BaseModel as BaseModelV1, Field

from ix.utils.importlib import import_class

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
    """Mock input for the mock runnable"""

    value: str = Field(description="this is a mock value", default="input")


class MockRunnable(Runnable[MockRunnableInput, Output], BaseModelV1):
    """Mock runnable that returns a default value"""

    name: str = "default"
    value: Any = "output"
    func_class_path: Optional[str] = None

    # instance state that can be used to store data between invocations
    # this is useful for tracking state while looping.
    state: dict[str, Any] = Field(default_factory=dict)

    def invoke(
        self,
        input: MockRunnableInput,
        config: Optional[RunnableConfig] = None,
    ) -> dict:
        # conditionally use a custom function to process the input
        if self.func_class_path:
            func = import_class(self.func_class_path)
            return func(input=input, config=config, state=self.state)

        # default return value
        if isinstance(input, dict):
            output = deepcopy(input)
            output[self.name] = self.value
            return output

        return {
            "input": input,
            self.name: self.value,
        }
