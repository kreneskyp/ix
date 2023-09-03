import logging
from typing import Optional
from uuid import UUID

from asgiref.sync import sync_to_async
from django.db.models import Q
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ix.chains.models import Chain

from ix.api.chains.types import (
    Chain as ChainPydantic,
    ChainQueryPage,
    CreateChain,
)


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
