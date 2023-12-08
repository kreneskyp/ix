from functools import reduce
from operator import or_
from typing import Dict, Any, List, Tuple, Optional, Iterator, AsyncIterator

from langchain.schema.runnable import (
    Runnable,
    RunnableParallel,
    RunnableBranch,
    RunnableSequence,
    RunnablePassthrough,
    RunnableSerializable,
    RunnableConfig,
)
from langchain.schema.runnable.base import Other, RunnableEach
from langchain.schema.runnable.utils import Input, Output

from ix.api.chains.types import InputConfig
from ix.chains.loaders.context import IxContext


def init_pass_through() -> RunnablePassthrough:
    """Helper to convert a RunnablePassthrough into a RunnablePassthrough."""
    return RunnablePassthrough()


def init_sequence(steps: List[Runnable[Input, Output]]) -> RunnableSequence:
    """Helper to convert a sequence of RunnableSerializable into a RunnableSequence."""
    if not steps:
        raise ValueError("sequential_nodes must have at least one element")

    return reduce(or_, steps)


def init_parallel(steps: Dict[str, Any | Runnable[Input, Output]]) -> RunnableParallel:
    """
    RunnableParallel is constructed by mapping RunnableSerializable to output
    keys. The config keys are dynamic and depends on the specific logic being
    implemented by the user. This function routes the RunnableSerializable
    passed in to a new RunnableParallel object.
    """
    return RunnableParallel(steps)


def init_each(
    workflow: RunnableSerializable[List[Input], List[Output]]
) -> RunnableEach:
    return RunnableEach(bound=workflow)


def init_branch(
    default: Runnable[Input, Output],
    branches: List[Tuple[str, Runnable[Input, Output]]],
) -> RunnableBranch:
    """
    TODO: need to make a final decision on how to connect decision functions to the branches.
          can either use a prior REPL, LLM, or a decision function embedded here somehow.
          - embedding is most convenient
          - separating is most flexible
    """
    return RunnableBranch(
        *[
            (lambda x, k=key: x.get(k, False), value)
            for key, value in branches
            if isinstance(value, Runnable)
        ],
        default,
    )


class InputMask(RunnableSerializable[Input, Output]):
    """Reduce input to the value of a single key."""

    key: str

    def invoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ):
        return input[self.key]


class RunnableProxy(Runnable[Input, Output]):
    # runnable_class: Type[Runnable]
    node: Any  # : ChainNode
    input_config: InputConfig
    context: IxContext
    # proxy_inputs: List[str]

    def build_runnable(self, input: Input) -> Runnable:
        """
        Build a runnable using inputs that are passed in. This delays the
        creation of the runnable until the input is available.
        """
        from ix.chains.loaders.core import load_node

        # TODO: push this into load_node / format_config()
        # build config with values from input
        config = self.node.config.copy()
        for key in self.input_config.to_config:
            if key not in input:
                raise ValueError(f"Missing input key: {key}")
            config[key] = input[key]

        # HAX: Set merged config on object. This alters the objects but
        #      doesn't write to the db.
        self.node.config = config

        # TODO: variables formats config for template, doesn't work here.
        return load_node(self.node, context=self.context, variables=input)

        # TODO: bind happens after, but it's part of IxNode.
        #     : need to align usage of node objects.

        # return self.runnable_class(**config)

    def invoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        runnable = self.build_runnable(input)
        return runnable.invoke(input, config)

    async def ainvoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        runnable = self.build_runnable(input)
        return await runnable.ainvoke(input, config)

    def transform(
        self,
        input: Iterator[Dict[str, Any]],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Iterator[Dict[str, Any]]:
        runnable = self.build_runnable(input)
        return runnable.transform(input, config)

    async def atransform(
        self,
        input: AsyncIterator[Dict[str, Any]],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        runnable = self.build_runnable(input)

        async def input_aiter() -> AsyncIterator[Other]:
            yield input

        async for chunk in runnable.atransform(input_aiter(), config, **kwargs):
            yield chunk

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
