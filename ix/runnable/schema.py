import json
from typing import Any, Optional

from langchain.schema.runnable import (
    RunnableSerializable,
    RunnableConfig,
)
from langchain.schema.runnable.utils import Input, Output
from pydantic import BaseModel


class SchemaOutput(BaseModel):
    name: str
    description: str
    parameters: Any


class Schema(RunnableSerializable[Input, Output]):
    """Returns a schema defined by configuration when invoked.

    This is a simple way to pass in a configuration in a consistent
    way to a runnable.
    """

    name: str
    description: str
    parameters: Any

    def __repr__(self):
        return f"Schema(name={self.name!r})"

    def __str__(self):
        return f"Schema(name={self.name})"

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Is this class serializable?"""
        return True

    def invoke(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
        **kwargs: Optional[Any],
    ) -> Output:
        if isinstance(self.parameters, str):
            return json.loads(self.parameters)
        return self.parameters

    async def ainvoke(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
        **kwargs: Optional[Any],
    ) -> Output:
        if isinstance(self.parameters, str):
            parameters = json.loads(self.parameters)
        else:
            parameters = self.parameters
        return {
            "name": self.name,
            "description": self.description,
            "parameters": parameters,
        }
