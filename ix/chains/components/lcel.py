from typing import Dict, Any, List

from langchain.schema.runnable import (
    RunnableParallel,
    RunnableSerializable,
    RunnableBranch,
    RunnableSequence,
    RunnablePassthrough,
)
from langchain.schema.runnable.utils import Input, Output


def init_runnable_sequence(
    sequential_nodes: List[RunnableSerializable[Input, Output]]
) -> RunnableSequence:
    """Helper to convert a sequence of RunnableSerializable into a RunnableSequence."""
    if not sequential_nodes:
        raise ValueError("sequential_nodes must have at least one element")

    return RunnableSequence(
        first=sequential_nodes[0],
        middle=(sequential_nodes[-1] if len(sequential_nodes) > 1 else []),
        last=(
            sequential_nodes[1:-1]
            if len(sequential_nodes) > 2
            else RunnablePassthrough()
        ),
    )


def init_parallel(
    **kwargs: Dict[str, Any | RunnableSerializable[Input, Output]]
) -> RunnableParallel:
    """
    RunnableParallel is constructed by mapping RunnableSerializable to output
    keys. The config keys are dynamic and depends on the specific logic being
    implemented by the user. This function routes the RunnableSerializable
    passed in to a new RunnableParallel object.
    """
    return RunnableParallel(
        steps={
            key: value
            for key, value in kwargs.items()
            if isinstance(value, RunnableSerializable)
        }
    )


def init_branch(
    default:  RunnableSerializable[Input, Output], **kwargs: Dict[str, RunnableSerializable[Input, Output]]
) -> RunnableBranch:
    """
    TODO: need to make a final decision on how to connect decision functions to the branches.
          can either use a prior REPL, LLM, or a decision function embedded here somehow.
          - embedding is most convenient
          - separating is most flexible
    """
    return RunnableBranch(
        [
            (lambda key: key, value)
            for key, value in kwargs.items()
            if isinstance(value, RunnableSerializable)
        ],
        default,
    )
