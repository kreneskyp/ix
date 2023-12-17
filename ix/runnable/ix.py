from typing import Dict, Any, Optional, Iterator, AsyncIterator, List, Type
from uuid import UUID

from langchain.schema.runnable import RunnableSerializable, RunnableConfig, Runnable
from langchain.schema.runnable.base import Other
from langchain.schema.runnable.utils import Input, Output
from pydantic import BaseModel

from ix.chains.loaders.context import IxContext


class IxNode(RunnableSerializable[Input, Output]):
    """
    Custom node that integrates runnables into the IX flow.

    Provides:
    - applies bindings to child runnable before invoking.
      Runs at input time to allow for dynamic bindings from
      input.
    - handles mapping input to the child runnable.
    - Provides IX context for access to full history of flow.
      and other services.
    - adds IX hooks for streaming status and log.
    """

    # TODO: does this need to be Runnable or RunnableSerializable?
    # Runnable fixes some tests
    node_id: UUID
    child: Runnable
    bind_points: List[str]
    config: Dict[str, Any]
    context: IxContext

    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        return f"IX::{repr(self.child)}"

    def __repr__(self):
        return f"IX::{repr(self.child)}"

    def get_input_schema(
        self, config: Optional[RunnableConfig] = None
    ) -> Type[BaseModel]:
        return self.child.get_input_schema(config)

    def get_output_schema(
        self, config: Optional[RunnableConfig] = None
    ) -> Type[BaseModel]:
        return self.child.get_output_schema(config)

    def build_runnable(self, input: Input) -> Runnable:
        """
        Build a runnable using inputs that are passed in. This delays the
        creation of the runnable until the input is available.
        """
        to_bind = {}
        for key in self.bind_points:
            # TODO: consider adding filter for ChainNode.input_fields
            if key in input:
                to_bind[key] = input.pop(key)
            elif key in self.config:
                to_bind[key] = self.config[key]

        if to_bind:
            return self.child.bind(**to_bind)
        return self.child

    def invoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Output:
        runnable = self.build_runnable(input)
        return runnable.invoke(input, config, **kwargs)

    async def ainvoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Output:
        listener = self.context.get_listener(self.node_id)
        listener.on_start(input=input)
        runnable = self.build_runnable(input)

        # unpack input if it's a dict
        if isinstance(input, dict) and "in" in input:
            input = input["in"]

        try:
            response = await runnable.ainvoke(input, config, **kwargs)
        except Exception as e:
            await listener.on_error(exception=e)
            raise
        await listener.aon_end(
            output=response,
        )
        return response

    def stream(
        self, input: Other, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> Iterator[Other]:
        runnable = self.build_runnable(input)
        return runnable.stream(input, config)

    async def astream(
        self,
        input: Other,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> AsyncIterator[Other]:
        runnable = self.build_runnable(input)

        async def input_aiter() -> AsyncIterator[Other]:
            yield input

        async for chunk in runnable.astream(input_aiter(), config, **kwargs):
            yield chunk
