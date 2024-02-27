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
from langgraph.graph import StateGraph, END

from ix.chains.models import ChainNode
from ix.data.models import Schema
from ix.utils.json_schema import jsonschema_to_typeddict


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


def init_graph(
    graph_root: ChainNode,
    action: Runnable[Input, Output],
    conditional: Runnable[Input, Output],
    nodes: List[Tuple[str, Runnable[Input, Output]]],
    entry_point: str = "start",
    loops: List[str] = [],
    ends: List[str] = [],
) -> Runnable:
    """
    Init a LangGraph graph
    """
    # Init graph using schema
    schema_id = graph_root.config["schema_id"]
    schema = Schema.objects.get(id=schema_id)
    state_model = jsonschema_to_typeddict(schema.value)
    workflow = StateGraph(state_model)

    # default map. END is always available.
    conditional_map = {"end": END}

    # add all nodes to the graph
    for name, node in nodes:
        workflow.add_node(name, node)
        conditional_map[name] = name

    # Add the action as entry_node or a passthrough if not present
    # The pass through turns the node into a pure conditional,
    # i.e. a simple decision node (flowchart diamond)
    workflow.add_node(entry_point, action or init_pass_through())

    # map the entry point
    workflow.set_entry_point(entry_point)
    workflow.add_conditional_edges(
        entry_point,
        lambda input: conditional.invoke(input),
        conditional_map,
    )

    # add edges to END nodes
    for node_name in ends:
        workflow.add_edge(node_name, END)

    # add loops back to the conditional
    for node_name in loops:
        workflow.add_edge(node_name, entry_point)

    return workflow.compile()
