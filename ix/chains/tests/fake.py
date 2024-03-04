import uuid
from typing import List, Dict, Tuple, Any, TypedDict

from asgiref.sync import sync_to_async
from langchain_core.messages import AIMessage
from langchain_core.runnables.utils import Input

from ix.chains.fixture_src.lcel import (
    RUNNABLE_MAP_CLASS_PATH,
    RUNNABLE_BRANCH_CLASS_PATH,
    LANGGRAPH_STATE_MACHINE_CLASS_PATH,
    LANGGRAPH_END_CLASS_PATH,
)
from ix.chains.loaders.core import (
    MapPlaceholder,
    BranchPlaceholder,
    find_roots,
    StateMachinePlaceholder,
)
from ix.chains.models import Chain, ChainNode, ChainEdge, NodeType
from ix.chains.tests.mock_runnable import MOCK_RUNNABLE_CLASS_PATH
from faker import Faker

from ix.data.models import Schema
from ix.data.tests.fake import fake_schema

fake = Faker()


def fake_chain(**kwargs) -> Chain:
    """
    Create a fake chain with a root ChainNode.
    """
    chain_kwargs = dict(
        id=uuid.uuid4(),
        name=fake.unique.name(),
        description=fake.text(),
        user=kwargs.get("user", None),
        group=kwargs.get("group", None),
    )
    chain_kwargs.update(kwargs)
    chain = Chain.objects.create(**chain_kwargs)
    return chain


async def afake_chain(**kwargs) -> Chain:
    """
    Create a fake chain with a root ChainNode.
    """
    return await sync_to_async(fake_chain)(**kwargs)


MOCK_RUNNABLE = {
    "class_path": "ix.runnable.prompt.ChatPrompt",
    "config": {
        "value": "default",
    },
}


def fake_chain_node(**kwargs) -> ChainNode:
    """
    Create a fake chain node.
    """
    chain = kwargs.get("chain", fake_chain())
    config = kwargs.get("config", MOCK_RUNNABLE)
    root = kwargs.get("root", True)
    return ChainNode.objects.create_from_config(
        chain=chain,
        root=root,
        config=config,
    )


async def afake_chain_node(**kwargs):
    """
    Create a fake chain node.
    """
    return await sync_to_async(fake_chain_node)(**kwargs)


def fake_root(**kwargs) -> ChainNode:
    """
    Create a fake root chain node.
    """
    config = kwargs.pop(
        "config",
        {
            "class_path": "__ROOT__",
            "config": {},
        },
    )
    return fake_chain_node(root=True, config=config, **kwargs)


async def afake_root(**kwargs):
    """
    Create a fake root chain node.
    """
    return await sync_to_async(fake_root)(**kwargs)


def fake_root_edge(chain: Chain, root: ChainNode, target: ChainNode) -> ChainEdge:
    return fake_chain_edge(
        chain=chain,
        source=root,
        target=target,
        source_key="inputs",
        target_key="in",
    )


async def afake_root_edge(**kwargs):
    return await sync_to_async(fake_root_edge)(**kwargs)


def fake_runnable(name="default", value=0, config=None, **kwargs):
    """
    Create a fake runnable.
    """
    options = dict(
        config={
            "class_path": MOCK_RUNNABLE_CLASS_PATH,
            "config": dict(name=name, value=value, **(config or {})),
        },
    )
    return fake_chain_node(**options, **kwargs)


def afake_runnable(name="default", value=0, **kwargs):
    """
    Create a fake runnable.
    """
    return sync_to_async(fake_runnable)(name=name, value=value, **kwargs)


def fake_chain_edge(**kwargs):
    if "key" in kwargs:
        raise ValueError("key is deprecated, use target_key instead")

    chain = kwargs.get("chain", fake_chain())

    source_node = kwargs.get("source")
    if source_node is None:
        source_node = fake_chain_node(chain=chain)

    target_node = kwargs.get("target")
    if target_node is None:
        target_node = fake_chain_node(chain=chain)

    edge = ChainEdge.objects.create(
        source=source_node,
        target=target_node,
        source_key=kwargs.get("source_key", source_node.node_type.type),
        target_key=kwargs.get("target_key", "default_key"),
        chain=chain,
        input_map=kwargs.get("input_map", {}),
        relation=kwargs.get("relation", "LINK"),
    )

    return edge


async def afake_chain_edge(**kwargs):
    """
    Create a fake chain edge.
    """
    return await sync_to_async(fake_chain_edge)(**kwargs)


def fake_node_sequence(
    chain: Chain, nodes: List[ChainNode] = None, n: int = 2, root: int = True
) -> List[ChainNode]:
    """Fake a sequence of ChainNode connected by edges

    Note that this does not create a RunnableSequence node. Sequences are
    represented implicitly by the edges. An explicit RunnableSequence node
    is not needed.
    """
    chain = chain or fake_chain()
    nodes = nodes or [
        fake_runnable(chain=chain, name=f"sequence_{i}", value=i, root=root and i == 0)
        for i in range(n)
    ]
    first_node = nodes[0]

    if isinstance(first_node, MapPlaceholder):
        current_node = first_node.node
    elif isinstance(first_node, BranchPlaceholder):
        raise ValueError(
            "Build sequence for branch's branches instead of including branch in sequence"
        )
    else:
        current_node = first_node

    for node in nodes[1:]:
        if isinstance(node, MapPlaceholder):
            # Create edges to the roots of every branch within the map.
            # The nodes should already be connected correctly internally.
            # Lastly, connect the outgoing edge to the map node itself.
            for map_root in find_roots(node):
                fake_chain_edge(
                    chain=chain,
                    source=current_node,
                    target=map_root,
                    source_key="out",
                    target_key="in",
                )
            current_node = node.node
        elif isinstance(node, BranchPlaceholder):
            raise ValueError(
                "Build sequence for branch's branches instead of including branch in sequence"
            )
        else:
            fake_chain_edge(
                chain=chain,
                source=current_node,
                target=node,
                source_key="out",
                target_key="in",
            )
            current_node = node
    return nodes


async def afake_node_sequence(**kwargs) -> List[ChainNode]:
    """Fake a sequence of ChainNode connected by edges"""
    return await sync_to_async(fake_node_sequence)(**kwargs)


def fake_node_dict(chain: Chain, keys: List[str], root=True) -> Dict[str, ChainNode]:
    """Fake a map of ChainNode connected by edges"""
    chain = chain or fake_chain()
    node_map = {}
    for key in keys:
        node = fake_runnable(chain=chain, name=key, root=root)
        node_map[key] = node
    return node_map


def afake_node_dict(**kwargs) -> Dict[str, ChainNode]:
    """Fake a map of ChainNode connected by edges"""
    return sync_to_async(fake_node_dict)(**kwargs)


def fake_node_map(
    chain: Chain,
    input_node: ChainNode = None,
    nodes: Dict[str, ChainNode] = None,
    root: bool = True,
) -> MapPlaceholder:
    """Add ChainEdges to match the structure of a dict of ChainNodes"""
    node_map = nodes or fake_node_dict(chain, ["a", "b", "c"], root=root)

    map_type = NodeType.objects.get(class_path=RUNNABLE_MAP_CLASS_PATH)
    map_node = ChainNode.objects.create(
        chain=chain,
        class_path=RUNNABLE_MAP_CLASS_PATH,
        node_type=map_type,
        root=False,
        config={
            "steps": list(node_map.keys()),
            "steps_hash": [str(uuid.uuid4()) for _ in range(len(node_map))],
        },
    )

    for map_key, node in node_map.items():
        if isinstance(node, MapPlaceholder):
            first_node = node.node
            source = node.node
        elif isinstance(node, list):
            first_node = node[0]
            source = node[-1]
        else:
            first_node = node
            source = node

        if input_node is not None:
            fake_chain_edge(
                chain=chain,
                source=input_node,
                target=first_node,
                source_key="out",
                target_key="in",
                relation="LINK",
            )

        # calculate target from steps hash_list
        index_of_key = map_node.config["steps"].index(map_key)
        key_hash = map_node.config["steps_hash"][index_of_key]

        ChainEdge.objects.create(
            source=source,
            target=map_node,
            source_key="out",
            target_key=key_hash,
            chain=chain,
            relation="LINK",
        )

    return MapPlaceholder(node=map_node, map=node_map)


async def afake_node_map(**kwargs) -> MapPlaceholder:
    """Add ChainEdges to match the structure of a dict of ChainNodes"""
    return await sync_to_async(fake_node_map)(**kwargs)


Branch = Tuple[str, ChainNode]
EncodedBranch = Branch


class BranchMeta(TypedDict):
    """Metadata to describe a branch config."""

    name: str
    description: str


def build_branches(
    class_path: str,
    chain: Chain = None,
    branches: List[Tuple[str | BranchMeta, ChainNode]] = None,
    root: bool = True,
    edge_type: str = "LINK",
    config: Dict[str, Any] = None,
) -> Tuple[ChainNode, List[Branch], List[EncodedBranch]]:
    """Generic method for all branching types"""
    chain = chain or fake_chain()

    branch_keys = ["a", "b", "c"] if branches is None else [key for key, _ in branches]
    branch_uuids = [str(uuid.uuid4()) for _ in range(len(branch_keys))]

    branch_type = NodeType.objects.get(class_path=class_path)
    _config = {
        "branches": branch_keys,
        "branches_hash": branch_uuids,
    }
    _config.update(config or {})
    branch_node = ChainNode.objects.create(
        chain=chain,
        class_path=class_path,
        node_type=branch_type,
        root=root,
        config=_config,
    )

    branches = branches or [
        (key, fake_runnable(chain=chain, name=key, root=False)) for key in branch_keys
    ]

    # encode branches with uuids for edges
    encoded_branches = [
        (branch_uuids[i], branch_node) for i, [key, branch_node] in enumerate(branches)
    ]

    for branch_uuid, branch in encoded_branches:
        for branch_root in find_roots(branch):
            fake_chain_edge(
                source=branch_node,
                target=branch_root,
                source_key=branch_uuid,
                target_key="in",
                relation=edge_type,
            )

    return branch_node, branches, encoded_branches


def fake_node_branch(
    chain: Chain,
    default: ChainNode = None,
    branches: List[Tuple[str, ChainNode]] = None,
    root: bool = True,
) -> BranchPlaceholder:
    """Fake a branch of ChainNode connected by edges"""
    chain = chain or fake_chain()

    branch_node, branches, encoded_branches = build_branches(
        RUNNABLE_BRANCH_CLASS_PATH,
        chain,
        branches=branches,
        root=root,
        edge_type="LINK",
    )

    default = default or fake_runnable(chain=chain, name="default", root=False)
    for branch_root in find_roots(default):
        fake_chain_edge(
            source=branch_node,
            target=branch_root,
            source_key="default",
            target_key="in",
            relation="LINK",
        )

    return BranchPlaceholder(
        node=branch_node,
        default=default,
        branches=branches,
    )


AGENT_STATE_SCHEMA = {
    "title": "AgentState",
    "description": "State for a basic conversational agent",
    "properties": {
        "messages": {
            "type": "array",
            "items": {"type": "#/def/BaseMessage"},
            "operation": "add",
        },
    },
    "definitions": {
        "BaseMessage": {
            "title": "BaseMessage",
            "description": "The base abstract Message class.\n\nMessages are the inputs and outputs of ChatModels.",
            "class_path": "langchain_core.messages.BaseMessage",
            "type": "object",
            "properties": {
                "content": {
                    "title": "Content",
                    "anyOf": [
                        {"type": "string"},
                        {
                            "type": "array",
                            "items": {
                                "anyOf": [{"type": "string"}, {"type": "object"}]
                            },
                        },
                    ],
                },
                "additional_kwargs": {"title": "Additional Kwargs", "type": "object"},
                "type": {"title": "Type", "type": "string"},
            },
            "required": ["content", "type"],
        }
    },
}


def fake_state_machine_schema() -> Schema:
    """fake method for creating a schema for a state machine"""
    return fake_schema(
        name=AGENT_STATE_SCHEMA["title"],
        type="json",
        description=AGENT_STATE_SCHEMA["description"],
        value=AGENT_STATE_SCHEMA,
    )


def _state_machine(input: Input, config: dict, state: dict, **kwargs):
    """mock function for state machine conditional with a predetermined sequence
    of states.

    Uses config["responses"] to determine the next state. END is sent after all
    responses are used or if none were configured.
    """
    current = state.get("current", 0)
    responses = config.get("responses", [])
    if current < len(responses):
        state["current"] = current + 1
        return responses[current]
    return "end"


def _state_machine_action(config, **kwargs):
    """mock function for state machine action"""
    return {"messages": [AIMessage(content="mock statemachine action")]}


STATE_MACHINE_ACTION = "ix.chains.tests.fake._state_machine_action"
STATE_MACHINE_CONDITIONAL = "ix.chains.tests.fake._state_machine"


def fake_state_machine_conditional() -> Chain:
    """fake method for creating a conditional for a state machine."""
    chain = fake_chain()
    fake_runnable(
        chain=chain,
        config=dict(func_class_path=STATE_MACHINE_CONDITIONAL),
        root=True,
    )
    return chain


def fake_state_machine_action() -> Chain:
    """fake method for creating an action for a state machine"""
    chain = fake_chain()
    fake_runnable(
        chain=chain,
        config=dict(func_class_path=STATE_MACHINE_ACTION),
        root=True,
    )
    return chain


def fake_node_state_machine(
    chain: Chain,
    branches: List[Tuple[str, ChainNode]] = None,
    root: bool = True,
    loops: List[str] = None,
) -> StateMachinePlaceholder:
    """Fake a LangGraph of ChainNode connected by edges"""

    schema: Schema = fake_state_machine_schema()
    conditional: Chain = fake_state_machine_conditional()
    action: Chain = fake_state_machine_action()

    chain = chain or fake_chain()
    branch_node, branches, encoded_branches = build_branches(
        LANGGRAPH_STATE_MACHINE_CLASS_PATH,
        chain,
        branches=branches,
        root=root,
        edge_type="GRAPH",
        config={
            "schema_id": str(schema.id),
            "conditional_id": str(conditional.id),
            "action_id": str(action.id),
        },
    )
    assert len(branches) > 0, "State machine must have at least one branch"

    # all branches loop by default
    branches = [(meta["name"], node) for meta, node in branches]
    loops = [k for k, v in branches] if loops is None else loops

    # create loop edges
    for branch_key, branch_leaf in branches:
        if branch_key in loops:
            if isinstance(branch_leaf, list):
                branch_leaf = branch_leaf[-1]

            fake_chain_edge(
                source=branch_leaf,
                target=branch_node,
                source_key=branch_key,
                target_key="in",
                relation="GRAPH",
            )

    return StateMachinePlaceholder(
        node=branch_node,
        branches=branches,
        loops=loops,
    )


async def afake_node_state_machine(**kwargs) -> StateMachinePlaceholder:
    """Fake a branch of ChainNode connected by edges"""
    return await sync_to_async(fake_node_state_machine)(**kwargs)


def fake_graph_end(**kwargs) -> ChainNode:
    """
    Create a fake graph END node
    """
    config = kwargs.pop(
        "config",
        {
            "class_path": LANGGRAPH_END_CLASS_PATH,
            "config": {},
        },
    )
    return fake_chain_node(root=False, config=config, **kwargs)


async def afake_graph_end(**kwargs) -> ChainNode:
    """
    Create a fake graph END node
    """
    return await sync_to_async(fake_graph_end)(**kwargs)


async def afake_node_branch(**kwargs) -> BranchPlaceholder:
    """Fake a branch of ChainNode connected by edges"""
    return await sync_to_async(fake_node_branch)(**kwargs)
