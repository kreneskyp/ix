import logging
from uuid import UUID

from django.db.models import Q
from fastapi import APIRouter, HTTPException

from ix.agents.models import Agent
from ix.api.chains.endpoints import DeletedItem
from ix.api.editor.types import (
    UpdateEdge,
    GraphModel,
    UpdateNode,
    UpdatedRoot,
    AddNode,
    UpdateRoot,
)
from ix.chains.models import Chain, ChainNode, NodeType, ChainEdge

from ix.api.chains.types import (
    Chain as ChainPydantic,
)
from ix.api.editor.types import PositionUpdate
from ix.api.components.types import NodeType as NodeTypePydantic
from ix.api.chains.types import Node as NodePydantic
from ix.api.chains.types import Edge as EdgePydantic


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/chains/{chain_id}/set_root", response_model=UpdatedRoot, tags=["Chain Editor"]
)
async def set_chain_root(chain_id: UUID, update_root: UpdateRoot):
    # update old roots:
    old_roots = ChainNode.objects.filter(chain_id=chain_id, root=True)
    old_root_ids = [
        str(node_id) async for node_id in old_roots.values_list("id", flat=True)
    ]
    await old_roots.aupdate(root=False)
    node_id = update_root.node_id
    if node_id:
        new_root = await ChainNode.objects.aget(id=node_id)
        new_root.root = True
        await new_root.asave(update_fields=["root"])
        new_root_id = str(new_root.id)

    else:
        new_root_id = None

    return UpdatedRoot(old_roots=old_root_ids, root=new_root_id)


@router.post("/chains/nodes", response_model=NodePydantic, tags=["Chain Editor"])
async def add_chain_node(node: AddNode):
    if not node.chain_id:
        chain = Chain(name="Unnamed", description="")
        await chain.asave()
        node.chain_id = chain.id

    node_type = await NodeType.objects.aget(class_path=node.class_path)
    new_node = ChainNode(node_type=node_type, **node.dict(exclude={"edges"}))
    await new_node.asave()

    # add edges to property connectors
    if node.edges:
        node_edges = []
        for datum in node.edges:
            # special case for edges to root pseudo-component
            if datum.source_id == "root":
                new_node.root = True
                await new_node.asave(update_fields=["root"])
                continue

            edge = ChainEdge(
                id=datum.id,
                key=datum.key,
                source_id=datum.source_id or new_node.id,
                target_id=datum.target_id or new_node.id,
                chain_id=node.chain_id,
                relation="LINK" if datum.key in {"in", "out"} else "PROP",
            )
            node_edges.append(edge)
        if node_edges:
            await ChainEdge.objects.abulk_create(node_edges)

    return NodePydantic.from_orm(new_node)


@router.put(
    "/chains/nodes/{node_id}", response_model=NodePydantic, tags=["Chain Editor"]
)
async def update_chain_node(node_id: UUID, data: UpdateNode):
    try:
        existing_node = await ChainNode.objects.aget(id=node_id)
    except ChainNode.DoesNotExist:
        raise HTTPException(status_code=404, detail="Node not found")
    as_dict = data.dict()
    for field, value in as_dict.items():
        setattr(existing_node, field, value)
    await existing_node.asave(update_fields=as_dict.keys())
    return NodePydantic.from_orm(existing_node)


@router.post(
    "/chains/nodes/{node_id}/position",
    response_model=NodePydantic,
    tags=["Chain Editor"],
)
async def update_chain_node_position(node_id: UUID, data: PositionUpdate):
    node = await ChainNode.objects.aget(id=node_id)
    node.position = data.dict()
    await node.asave(update_fields=["position"])
    return NodePydantic.from_orm(node)


@router.delete(
    "/chains/nodes/{node_id}", response_model=DeletedItem, tags=["Chain Editor"]
)
async def delete_chain_node(node_id: UUID):
    node = await ChainNode.objects.aget(id=node_id)
    if node:
        edges = ChainEdge.objects.filter(Q(source_id=node_id) | Q(target_id=node_id))
        await edges.adelete()
        await node.adelete()
    return DeletedItem(id=node_id)


@router.post("/chains/edges", response_model=EdgePydantic, tags=["Chain Editor"])
async def add_chain_edge(data: EdgePydantic):
    new_edge = ChainEdge(**data.dict())
    await new_edge.asave()
    return EdgePydantic.from_orm(new_edge)


@router.put(
    "/chains/edges/{edge_id}", response_model=EdgePydantic, tags=["Chain Editor"]
)
async def update_chain_edge(edge_id, data: UpdateEdge):
    try:
        existing_edge = await ChainEdge.objects.aget(id=edge_id)
    except ChainEdge.DoesNotExist:
        raise HTTPException(status_code=404, detail="Edge not found")
    as_dict = data.dict()
    for field, value in as_dict.items():
        setattr(existing_edge, field, value)
    await existing_edge.asave(update_fields=as_dict.keys())
    return EdgePydantic.from_orm(existing_edge)


@router.delete(
    "/chains/edges/{edge_id}", response_model=DeletedItem, tags=["Chain Editor"]
)
async def delete_chain_edge(edge_id: UUID):
    edge = await ChainEdge.objects.aget(id=edge_id)
    if edge:
        await edge.adelete()
    return DeletedItem(id=edge_id)


@router.get(
    "/chains/{chain_id}/graph", response_model=GraphModel, tags=["Chain Editor"]
)
async def get_chain_graph(chain_id: UUID):
    """Return chain and all it's nodes and edges."""
    chain = await Chain.objects.aget(id=chain_id)

    nodes = []
    node_queryset = ChainNode.objects.filter(chain_id=chain_id)
    async for node in node_queryset:
        nodes.append(NodePydantic.from_orm(node))

    edges = []
    edge_queryset = ChainEdge.objects.filter(chain_id=chain_id)
    async for edge in edge_queryset:
        edges.append(EdgePydantic.from_orm(edge))

    types_in_chain = NodeType.objects.filter(chainnode__chain_id=chain_id)
    types = [NodeTypePydantic.from_orm(node_type) async for node_type in types_in_chain]

    return GraphModel(
        chain=ChainPydantic.from_orm(chain),
        nodes=nodes,
        edges=edges,
        types=types,
    )


@router.get(
    "/chains/{chain_id}/test/chat", response_model=GraphModel, tags=["Chain Editor"]
)
async def get_test_chat():
    # create an agent if there is no agent
    agent = await Agent.objects.aget(name="Test Agent")
