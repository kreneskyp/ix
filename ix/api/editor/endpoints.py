import asyncio
import logging
from uuid import UUID

from django.db.models import Q
from fastapi import APIRouter, HTTPException

from ix.agents.models import Agent
from ix.api.chains.endpoints import (
    DeletedItem,
    create_chain_instance,
    create_chain_chat,
)
from ix.api.chats.types import Chat as ChatPydantic
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
from ix.chat.models import Chat

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/chains/{chain_id}/set_root", response_model=UpdatedRoot, tags=["Chain Editor"]
)
async def set_chain_root(chain_id: UUID, update_root: UpdateRoot):
    # update old roots:
    old_roots = ChainNode.objects.filter(chain_id=chain_id, root=True).exclude(
        id__in=update_root.node_ids
    )
    old_root_ids = [
        str(node_id) async for node_id in old_roots.values_list("id", flat=True)
    ]
    remove_roots = old_roots.aupdate(root=False)
    add_roots = ChainNode.objects.filter(
        id__in=update_root.node_ids, root=False
    ).aupdate(root=True)
    await asyncio.gather(remove_roots, add_roots)
    return UpdatedRoot(old_roots=old_root_ids, roots=update_root.node_ids)


@router.post("/chains/nodes", response_model=NodePydantic, tags=["Chain Editor"])
async def add_chain_node(node: AddNode):
    if not node.chain_id:
        chain = await create_chain_instance(
            name="Unnamed", description="", alias="Unnamed"
        )
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
                source_key=datum.source_key,
                target_key=datum.target_key,
                source_id=datum.source_id or new_node.id,
                target_id=datum.target_id or new_node.id,
                chain_id=node.chain_id,
                relation="LINK" if datum.target_key in {"in", "out"} else "PROP",
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

    # sync alias to chain object
    chain_pydantic = ChainPydantic.from_orm(chain)
    if chain.is_agent:
        agent = await Agent.objects.aget(chain_id=chain_id, is_test=False)
        chain_pydantic.alias = agent.alias

    return GraphModel(
        chain=chain_pydantic,
        nodes=nodes,
        edges=edges,
        types=types,
    )


@router.get(
    "/chains/{chain_id}/chat", response_model=ChatPydantic, tags=["Chain Editor"]
)
async def get_chain_chat(chain_id: UUID):
    """Return test chat instance for the chain"""
    try:
        chat = await Chat.objects.aget(lead__chain_id=chain_id, lead__is_test=True)
    except Chat.DoesNotExist:
        chain = await Chain.objects.aget(id=chain_id)
        chat = await create_chain_chat(chain)

    return ChatPydantic.from_orm(chat)
