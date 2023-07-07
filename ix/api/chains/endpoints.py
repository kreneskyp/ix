from typing import Optional, List, Literal
from uuid import UUID

from django.db.models import Q
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ix.chains.models import Chain, ChainNode, NodeType, ChainEdge

from ix.api.chains.types import Chain as ChainPydantic
from ix.api.chains.types import NodeType as NodeTypePydantic
from ix.api.chains.types import Node as NodePydantic
from ix.api.chains.types import Edge as EdgePydantic
from ix.api.chains.types import Position

router = APIRouter()


class DeletedItem(BaseModel):
    id: UUID


@router.get("/chains/", response_model=List[ChainPydantic])
async def get_chains():
    chains = Chain.objects.all()
    return [ChainPydantic.from_orm(chain) async for chain in chains]


@router.post("/chains/", response_model=ChainPydantic)
async def create_chain(chain: ChainPydantic):
    new_chain = Chain(**chain.dict())
    await new_chain.asave()
    return ChainPydantic.from_orm(new_chain)


@router.get("/chains/{chain_id}", response_model=ChainPydantic)
async def get_chain_detail(chain_id: UUID):
    try:
        chain = await Chain.objects.aget(id=chain_id)
    except Chain.DoesNotExist:
        raise HTTPException(status_code=404, detail="Chain not found")
    return ChainPydantic.from_orm(chain)


class UpdateChain(BaseModel):
    name: str
    description: str


@router.put("/chains/{chain_id}", response_model=ChainPydantic)
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


@router.delete("/chains/{chain_id}", response_model=DeletedItem)
async def delete_chain(chain_id: UUID):
    try:
        existing_chain = await Chain.objects.aget(id=chain_id)
    except Chain.DoesNotExist:
        raise HTTPException(status_code=404, detail="Chain not found")
    await existing_chain.adelete()
    return DeletedItem(id=chain_id)


@router.get("/node_types/", response_model=List[NodeTypePydantic])
async def get_node_types(search: Optional[str] = None):
    if search:
        node_types = NodeType.objects.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(type__icontains=search)
            | Q(class_path__icontains=search)
        )
    else:
        node_types = NodeType.objects.all()
    return [NodeTypePydantic.from_orm(node_type) async for node_type in node_types]


@router.get("/node_types/{node_type_id}", response_model=NodeTypePydantic)
async def get_node_type_detail(node_type_id: UUID):
    try:
        node_type = await NodeType.objects.aget(id=node_type_id)
    except NodeType.DoesNotExist:
        raise HTTPException(status_code=404, detail="Node type not found")
    return NodeTypePydantic.from_orm(node_type)


@router.post("/node_types/", response_model=NodeTypePydantic)
async def create_node_type(node_type: NodeTypePydantic):
    node_type_obj = NodeType(**node_type.dict())
    await node_type_obj.asave()
    return NodeTypePydantic.from_orm(node_type_obj)


@router.put("/node_types/{node_type_id}", response_model=NodeTypePydantic)
async def update_node_type(node_type_id: UUID, node_type: NodeTypePydantic):
    try:
        existing_node_type = await NodeType.objects.aget(id=node_type_id)
    except NodeType.DoesNotExist:
        raise HTTPException(status_code=404, detail="Node type not found")

    for field, value in node_type.dict(exclude_unset=True).items():
        setattr(existing_node_type, field, value)

    await existing_node_type.asave()
    return NodeTypePydantic.from_orm(existing_node_type)


@router.delete("/node_types/{node_type_id}", response_model=DeletedItem)
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


@router.post("/chain/{chain_id}/set_root/", response_model=UpdatedRoot)
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
    name: str
    description: str
    config: Optional[dict]
    position: Optional[Position]


@router.post("/chain/nodes", response_model=NodePydantic)
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


@router.put("/chain/nodes/{node_id}", response_model=NodePydantic)
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


@router.post("/chain/nodes/{node_id}/position", response_model=NodePydantic)
async def update_chain_node_position(node_id: UUID, position: Position):
    node = await ChainNode.objects.aget(id=node_id)
    node.position = position.dict()
    await node.asave(update_fields=["position"])
    return NodePydantic.from_orm(node)


@router.delete("/chain/nodes/{node_id}", response_model=DeletedItem)
async def delete_chain_node(node_id: UUID):
    node = await ChainNode.objects.aget(id=node_id)
    if node:
        edges = ChainEdge.objects.filter(Q(source_id=node_id) | Q(target_id=node_id))
        await edges.adelete()
        await node.adelete()
    return DeletedItem(id=node_id)


@router.post("/chain/edges", response_model=EdgePydantic)
async def add_chain_edge(edge: EdgePydantic):
    new_edge = ChainEdge(**edge.dict())
    await new_edge.asave()
    return EdgePydantic.from_orm(new_edge)


class UpdateEdge(BaseModel):
    source_id: UUID
    target_id: UUID
    key: str
    relation: Literal["LINK", "PROP"]
    input_map: Optional[dict]


@router.put("/chain/edges/{edge_id}", response_model=EdgePydantic)
async def update_chain_edge(edge_id: UUID, edge: UpdateEdge):
    try:
        existing_edge = await ChainEdge.objects.aget(id=edge_id)
    except ChainEdge.DoesNotExist:
        raise HTTPException(status_code=404, detail="Edge not found")
    as_dict = edge.dict()
    for field, value in as_dict.items():
        setattr(existing_edge, field, value)
    await existing_edge.asave(update_fields=as_dict.keys())
    return EdgePydantic.from_orm(existing_edge)


@router.delete("/chain/edges/{edge_id}", response_model=DeletedItem)
async def delete_chain_edge(edge_id: UUID):
    edge = await ChainEdge.objects.aget(id=edge_id)
    if edge:
        await edge.adelete()
    return DeletedItem(id=edge_id)


class GraphModel(BaseModel):
    chain: ChainPydantic
    nodes: List[NodePydantic]
    edges: List[EdgePydantic]


@router.get("/chain/{chain_id}/graph", response_model=GraphModel)
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

    return GraphModel(
        chain=ChainPydantic.from_orm(chain),
        nodes=nodes,
        edges=edges,
    )
