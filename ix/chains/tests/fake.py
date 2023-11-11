import uuid
from typing import List, Dict, Tuple

from asgiref.sync import sync_to_async

from ix.chains.fixture_src.lcel import (
    RUNNABLE_MAP_CLASS_PATH,
    RUNNABLE_BRANCH_CLASS_PATH,
)
from ix.chains.loaders.core import MapPlaceholder, BranchPlaceholder
from ix.chains.models import Chain, ChainNode, ChainEdge
from ix.chains.tests.mock_runnable import MOCK_RUNNABLE_CLASS_PATH
from faker import Faker

fake = Faker()


def fake_chain(**kwargs):
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


async def afake_chain(**kwargs):
    """
    Create a fake chain with a root ChainNode.
    """
    return await sync_to_async(fake_chain)(**kwargs)


MOCK_RUNNABLE = {
    "class_path": "langchain.prompts.chat.ChatPromptTemplate",
    "config": {
        "value": "default",
    },
}


def fake_chain_node(**kwargs):
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


def fake_runnable(name="default", value=0, **kwargs):
    """
    Create a fake runnable.
    """
    options = dict(
        config=kwargs.get(
            "config",
            {
                "class_path": MOCK_RUNNABLE_CLASS_PATH,
                "config": {
                    "name": name,
                    "value": value,
                },
            },
        ),
        **kwargs,
    )
    return fake_chain_node(**options)


def afake_runnable(name="default", value=0, **kwargs):
    """
    Create a fake runnable.
    """
    return sync_to_async(fake_runnable)(name=name, value=value, **kwargs)


def fake_chain_edge(**kwargs):
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
        key=kwargs.get("key", "in"),
        map_key=kwargs.get("map_key", None),
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


def find_roots(
    node: ChainNode | List[ChainNode] | MapPlaceholder | BranchPlaceholder,
) -> List[ChainNode]:
    """Finds the first node(s) for a node or node group.

    Used to find the node that should recieve the incoming edge when connecting
    the node group to a sequence
    """
    if isinstance(node, list):
        return [node[0]]
    elif isinstance(node, MapPlaceholder):
        nodes = []
        for mapped_node in node.map.values():
            nodes.extend(find_roots(mapped_node))
        return nodes
    elif isinstance(node, BranchPlaceholder):
        return [node.node]
    return [node]


def find_leaves(
    node: ChainNode | List[ChainNode] | MapPlaceholder | BranchPlaceholder,
) -> List[ChainNode]:
    """Finds the last node(s) for a node or node group.

    Used to find the node that should recieve the outgoing edge when connecting
    the node group to a sequence
    """
    if isinstance(node, list):
        return [node[-1]]
    elif isinstance(node, MapPlaceholder):
        nodes = []
        for mapped_node in node.map.values():
            nodes.extend(find_leaves(mapped_node))
        return nodes
    elif isinstance(node, BranchPlaceholder):
        nodes = [find_leaves(node.default)]
        for key, branch_node in node.branches:
            nodes.extend(find_leaves(branch_node))
        return nodes
    return [node]


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
                fake_chain_edge(chain=chain, source=current_node, target=map_root)
            current_node = node.node
        elif isinstance(node, BranchPlaceholder):
            raise ValueError(
                "Build sequence for branch's branches instead of including branch in sequence"
            )
        else:
            fake_chain_edge(chain=chain, source=current_node, target=node)
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
    map_node = ChainNode.objects.create(
        chain=chain,
        class_path=RUNNABLE_MAP_CLASS_PATH,
        root=False,
    )

    node_map = nodes or fake_node_dict(chain, ["a", "b", "c"], root=root)
    for map_key, node in node_map.items():
        if input_node is not None:
            fake_chain_edge(
                chain=chain,
                source=input_node,
                target=node,
                key="in",
                relation="LINK",
            )

        if isinstance(node, MapPlaceholder):
            source = node.node
        elif isinstance(node, list):
            source = node[-1]
        else:
            source = node

        ChainEdge.objects.create(
            source=source,
            target=map_node,
            key="steps",
            map_key=map_key,
            chain=chain,
            relation="LINK",
        )

    return MapPlaceholder(node=map_node, map=node_map)


async def afake_node_map(**kwargs) -> MapPlaceholder:
    """Add ChainEdges to match the structure of a dict of ChainNodes"""
    return await sync_to_async(fake_node_map)(**kwargs)


def fake_node_branch(
    chain: Chain,
    default: ChainNode = None,
    branches: List[Tuple[str, ChainNode]] = None,
    root: bool = True,
) -> BranchPlaceholder:
    """Fake a branch of ChainNode connected by edges"""
    chain = chain or fake_chain()

    branch_keys = ["a", "b", "c"] if branches is None else [key for key, _ in branches]

    branch_node = ChainNode.objects.create(
        chain=chain,
        class_path=RUNNABLE_BRANCH_CLASS_PATH,
        root=root,
        config={
            "branches": branch_keys,
        },
    )

    default = default or fake_runnable(chain=chain, name="default", root=False)
    branches = branches or [
        (key, fake_runnable(chain=chain, name=key, root=False)) for key in branch_keys
    ]

    for branch_root in find_roots(default):
        fake_chain_edge(
            source=branch_node, target=branch_root, key="default", relation="LINK"
        )

    for key, branch in branches:
        for branch_root in find_roots(branch):
            fake_chain_edge(
                source=branch_node, target=branch_root, key=key, relation="LINK"
            )

    return BranchPlaceholder(
        node=branch_node,
        default=default,
        branches=branches,
    )


async def afake_node_branch(**kwargs) -> BranchPlaceholder:
    """Fake a branch of ChainNode connected by edges"""
    return await sync_to_async(fake_node_branch)(**kwargs)
