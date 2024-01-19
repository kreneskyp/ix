import json
from typing import Any, Optional

from langchain.schema.runnable import (
    RunnableSerializable,
    RunnableConfig,
)
from langchain.schema.runnable.utils import Input, Output
from pydantic import BaseModel
from pydantic import UUID4
from ix.data.models import Schema
from ix.data.types import Schema as SchemaPydantic


class SchemaOutput(BaseModel):
    name: str
    description: str
    parameters: Any


class FunctionSchema(RunnableSerializable[Input, Output]):
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


class LoadSchema(RunnableSerializable[Input, SchemaPydantic]):
    """Get a schema from the IX schema registry"""

    schema_id: UUID4

    def invoke(
        self, input: Input, config: Optional[RunnableConfig] = None, **kwargs
    ) -> SchemaPydantic:
        instance = Schema.objects.get(pk=self.schema_id)
        return SchemaPydantic.model_validate(instance)

    async def ainvoke(
        self, input: Input, config: Optional[RunnableConfig] = None, **kwargs
    ) -> SchemaPydantic:
        instance = await Schema.objects.aget(pk=self.schema_id)
        return SchemaPydantic.model_validate(instance)


class SaveSchema(RunnableSerializable[SchemaPydantic, SchemaPydantic]):
    """Save a schema to the IX schema registry"""

    def invoke(
        self, input: SchemaPydantic, config: Optional[RunnableConfig] = None, **kwargs
    ) -> Output:
        schema = Schema.objects.create(**input.model_dump(exclude={"id"})).pk
        return SchemaPydantic.model_validate(schema)

    async def ainvoke(
        self, input: SchemaPydantic, config: Optional[RunnableConfig] = None, **kwargs
    ) -> Output:
        schema = await Schema.objects.acreate(**input.model_dump(exclude={"id"})).pk
        return SchemaPydantic.model_validate(schema)
