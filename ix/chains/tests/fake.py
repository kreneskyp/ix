import uuid
from typing import List, Dict, Tuple, Any

from asgiref.sync import sync_to_async

from ix.chains.fixture_src.lcel import (
    RUNNABLE_MAP_CLASS_PATH,
    RUNNABLE_BRANCH_CLASS_PATH,
)
from ix.chains.loaders.core import (
    MapPlaceholder,
    BranchPlaceholder,
    find_roots,
)
from ix.chains.models import Chain, ChainNode, ChainEdge, NodeType
from ix.chains.tests.mock_runnable import MOCK_RUNNABLE_CLASS_PATH
from faker import Faker

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


def build_branches(
    class_path: str,
    chain: Chain = None,
    branches: List[Tuple[str, ChainNode]] = None,
    root: bool = True,
    edge_type: str = "LINK",
    config: Dict[str, Any] = None,
) -> Tuple[ChainNode, List[Tuple[str, ChainNode]]]:
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

    return branch_node, branches


def fake_node_branch(
    chain: Chain,
    default: ChainNode = None,
    branches: List[Tuple[str, ChainNode]] = None,
    root: bool = True,
) -> BranchPlaceholder:
    """Fake a branch of ChainNode connected by edges"""
    chain = chain or fake_chain()

    branch_node, branches = build_branches(
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


async def afake_node_branch(**kwargs) -> BranchPlaceholder:
    """Fake a branch of ChainNode connected by edges"""
    return await sync_to_async(fake_node_branch)(**kwargs)
