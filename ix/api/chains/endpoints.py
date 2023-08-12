import logging
from typing import Optional, List
from uuid import UUID

from asgiref.sync import sync_to_async
from django.db.models import Q
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ix.chains.models import Chain, ChainNode, NodeType, ChainEdge

from ix.api.chains.types import (
    Chain as ChainPydantic,
    ChainQueryPage,
    PositionUpdate,
    NodeTypePage,
    CreateChain,
)
from ix.api.chains.types import NodeType as NodeTypePydantic
from ix.api.chains.types import Node as NodePydantic
from ix.api.chains.types import Edge as EdgePydantic
from ix.api.chains.types import Position


logger = logging.getLogger(__name__)
router = APIRouter()


class DeletedItem(BaseModel):
    id: UUID


@router.get("/chains/", response_model=ChainQueryPage, tags=["Chains"])
async def get_chains(search: Optional[str] = None, limit: int = 10, offset: int = 0):
    query = (
        Chain.objects.filter(Q(name__icontains=search))
        if search
        else Chain.objects.all()
    )
    query = query.order_by("-created_at")

    # punting on async implementation of pagination until later
    return await sync_to_async(ChainQueryPage.paginate)(
        output_model=ChainPydantic, queryset=query, limit=limit, offset=offset
    )


@router.post("/chains/", response_model=ChainPydantic, tags=["Chains"])
async def create_chain(chain: CreateChain):
    new_chain = Chain(**chain.dict())
    await new_chain.asave()
    return ChainPydantic.from_orm(new_chain)


@router.get("/chains/{chain_id}", response_model=ChainPydantic, tags=["Chains"])
async def get_chain_detail(chain_id: UUID):
    try:
        chain = await Chain.objects.aget(id=chain_id)
    except Chain.DoesNotExist:
        raise HTTPException(status_code=404, detail="Chain not found")
    return ChainPydantic.from_orm(chain)


class UpdateChain(BaseModel):
    name: str
    description: str


@router.put("/chains/{chain_id}", response_model=ChainPydantic, tags=["Chains"])
async def update_chain(chain_id: UUID, chain: UpdateChain):
    try:
        existing_chain = await Chain.objects.aget(id=chain_id)
    except Chain.DoesNotExist:
        raise HTTPException(status_code=404, detail="Chain not found")
    as_dict = chain.dict()
    for field, value in as_dict.items():
        setattr(existing_chain, field, value)
    await existing_chain.asave(update_fields=as_dict.keys())
    return ChainPydantic.from_orm(existing_chain)


@router.delete("/chains/{chain_id}", response_model=DeletedItem, tags=["Chains"])
async def delete_chain(chain_id: UUID):
    try:
        existing_chain = await Chain.objects.aget(id=chain_id)
    except Chain.DoesNotExist:
        raise HTTPException(status_code=404, detail="Chain not found")
    await existing_chain.adelete()
    return DeletedItem(id=chain_id)


@router.get("/node_types/", response_model=NodeTypePage, tags=["Components"])
async def get_node_types(
    search: Optional[str] = None, limit: int = 50, offset: int = 0
):
    if search:
        query = NodeType.objects.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(type__icontains=search)
            | Q(class_path__icontains=search)
        )
    else:
        query = NodeType.objects.all()

    # punting on async implementation of pagination until later
    return await sync_to_async(NodeTypePage.paginate)(
        output_model=NodeTypePydantic, queryset=query, limit=limit, offset=offset
    )


class NodeTypeDetail(NodeTypePydantic):
    config_schema: Optional[dict] = None


@router.get(
    "/node_types/{node_type_id}", response_model=NodeTypeDetail, tags=["Components"]
)
async def get_node_type_detail(node_type_id: UUID):
    try:
        node_type = await NodeType.objects.aget(id=node_type_id)
    except NodeType.DoesNotExist:
        raise HTTPException(status_code=404, detail="Node type not found")
    return NodeTypeDetail.from_orm(node_type)


@router.post("/node_types/", response_model=NodeTypePydantic, tags=["Components"])
async def create_node_type(node_type: NodeTypePydantic):
    node_type_obj = NodeType(**node_type.dict())
    await node_type_obj.asave()
    return NodeTypePydantic.from_orm(node_type_obj)


@router.put(
    "/node_types/{node_type_id}", response_model=NodeTypePydantic, tags=["Components"]
)
async def update_node_type(node_type_id: UUID, node_type: NodeTypePydantic):
    try:
        existing_node_type = await NodeType.objects.aget(id=node_type_id)
    except NodeType.DoesNotExist:
        raise HTTPException(status_code=404, detail="Node type not found")

    for field, value in node_type.dict(exclude_unset=True).items():
        setattr(existing_node_type, field, value)

    await existing_node_type.asave()
    return NodeTypePydantic.from_orm(existing_node_type)


@router.delete(
    "/node_types/{node_type_id}", response_model=DeletedItem, tags=["Components"]
)
async def delete_node_type(node_type_id: UUID):
    query = NodeType.objects.filter(id=node_type_id)
    if not await query.aexists():
        raise HTTPException(status_code=404, detail="Node type not found")

    await query.adelete()
    return DeletedItem(id=node_type_id)


class UpdatedRoot(BaseModel):
    root: Optional[UUID]
    old_roots: List[str]


class UpdateRoot(BaseModel):
    node_id: Optional[UUID]


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


class AddNode(BaseModel):
    id: Optional[UUID]
    chain_id: Optional[UUID]
    class_path: str
    name: Optional[str]
    description: Optional[str]
    config: Optional[dict]
    position: Optional[Position]


@router.post("/chains/nodes", response_model=NodePydantic, tags=["Chain Editor"])
async def add_chain_node(node: AddNode):
    if not node.chain_id:
        chain = Chain(name="Unnamed", description="")
        await chain.asave()
        node.chain_id = chain.id

    node_type = await NodeType.objects.aget(class_path=node.class_path)
    new_node = ChainNode(node_type=node_type, **node.dict())
    await new_node.asave()
    return NodePydantic.from_orm(new_node)


class UpdateNode(BaseModel):
    config: Optional[dict]
    name: Optional[str]
    description: Optional[str]
    position: Optional[Position]


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


class UpdateEdge(BaseModel):
    source_id: UUID
    target_id: UUID


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


class GraphModel(BaseModel):
    chain: ChainPydantic
    nodes: List[NodePydantic]
    edges: List[EdgePydantic]
    types: List[NodeTypePydantic]


@router.get("/chains/{chain_id}/graph", response_model=GraphModel, tags=["Chains"])
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
