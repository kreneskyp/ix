from functools import reduce
from operator import or_
from typing import Dict, Any, List, Tuple

from langchain.schema.runnable import (
    Runnable,
    RunnableParallel,
    RunnableBranch,
    RunnableSequence,
    RunnablePassthrough,
    RunnableSerializable,
)
from langchain.schema.runnable.base import RunnableEach
from langchain.schema.runnable.utils import Input, Output


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
