import logging
from typing import Optional
from uuid import UUID

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel


from ix.agents.models import Agent
from ix.chains.models import Chain
from ix.api.auth import get_request_user
from ix.api.chains.types import (
    Chain as ChainPydantic,
    ChainQueryPage,
    CreateChain,
    UpdateChain,
)
from ix.chat.models import Chat
from ix.task_log.models import Task

logger = logging.getLogger(__name__)
router = APIRouter()


class DeletedItem(BaseModel):
    id: UUID


@router.get(
    "/chains/",
    operation_id="get_chains",
    response_model=ChainQueryPage,
    tags=["Chains"],
)
async def get_chains(
    search: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    is_agent: Optional[bool] = None,
    user: AbstractUser = Depends(get_request_user),
):
    query = Chain.filtered_owners(user)

    if search:
        query = query.filter(Q(name__icontains=search))

    if is_agent is not None:
        query = query.filter(is_agent=is_agent)

    query = query.order_by("-created_at")

    # punting on async implementation of pagination until later
    return await sync_to_async(ChainQueryPage.paginate)(
        output_model=ChainPydantic, queryset=query, limit=limit, offset=offset
    )


async def create_chain_agent(chain: Chain, alias: str) -> Agent:
    """Create a non-test agent for a chain."""
    return await Agent.objects.acreate(
        name=chain.name,
        alias=alias,
        purpose=chain.description,
        chain=chain,
        is_test=False,
    )


async def create_chain_chat(chain: Chain) -> Chat:
    """Create a test chat for a chain."""

    # HAX: a shared fake user is used for all chains
    user_model = get_user_model()
    user = await user_model.objects.alatest("id")

    # Create objects for test chat. It's likely that most chains
    # will be tested in the chat. Better to create test chat
    # by default on chain creation where it's easy and optimize later.
    agent = await Agent.objects.acreate(
        name=chain.name,
        alias="test",
        purpose=chain.description,
        chain=chain,
        is_test=True,
    )
    task = await Task.objects.acreate(
        agent=agent,
        chain=chain,
        user=user,
    )
    return await Chat.objects.acreate(
        name=f"Test Chat: {chain.name}",
        lead=agent,
        task=task,
        is_test=True,
    )


async def create_chain_instance(**kwargs) -> Chain:
    """Create a chain. Includes creating a test agent, task, and chat."""

    alias = kwargs.pop("alias", "")
    chain = Chain(**kwargs)
    await chain.asave()

    # create test chat
    await create_chain_chat(chain)

    # create agent if chain is an agent.
    if chain.is_agent:
        await create_chain_agent(chain, alias)

    return chain


@router.post(
    "/chains/",
    operation_id="create_chain",
    response_model=ChainPydantic,
    tags=["Chains"],
)
async def create_chain(
    chain: CreateChain, user: AbstractUser = Depends(get_request_user)
):
    new_chain = await create_chain_instance(**chain.model_dump(), user=user)
    return ChainPydantic.model_validate(new_chain)


@router.get(
    "/chains/{chain_id}",
    operation_id="get_chain",
    response_model=ChainPydantic,
    tags=["Chains"],
)
async def get_chain_detail(
    chain_id: UUID, user: AbstractUser = Depends(get_request_user)
):
    query = Chain.filtered_owners(user)
    try:
        chain = await query.aget(id=chain_id)
    except Chain.DoesNotExist:
        raise HTTPException(status_code=404, detail="Chain not found")
    response = ChainPydantic.model_validate(chain)

    # fetch pass through properties so a second query isn't needed
    if chain.is_agent:
        agent = await Agent.objects.aget(chain=chain, is_test=False)
        response.alias = agent.alias

    return response


async def sync_chain_agent(chain: Chain, alias: str) -> None:
    """Sync the state of Chain and Agent objects.

    If chain.is_agent is True, then an agent should exist.
    Adjust the state of the agent to match the chain.
    """
    if chain.is_agent:
        if not await Agent.objects.filter(chain=chain).aexists():
            await create_chain_agent(chain, alias=alias)
        else:
            # sync properties to existing agent
            await Agent.objects.filter(chain=chain, is_test=False).aupdate(
                name=chain.name,
                alias=alias,
                purpose=chain.description,
            )
    else:
        # destroy agent if it exists
        if await Agent.objects.filter(chain=chain, is_test=False).aexists():
            await Agent.objects.filter(chain=chain, is_test=False).adelete()


@router.put(
    "/chains/{chain_id}",
    operation_id="update_chain",
    response_model=ChainPydantic,
    tags=["Chains"],
)
async def update_chain(
    chain_id: UUID, chain: UpdateChain, user: AbstractUser = Depends(get_request_user)
):
    query = Chain.filtered_owners(user)
    try:
        existing_chain = await query.aget(id=chain_id)
    except Chain.DoesNotExist:
        raise HTTPException(status_code=404, detail="Chain not found")
    as_dict = chain.model_dump(exclude={"alias"})
    for field, value in as_dict.items():
        setattr(existing_chain, field, value)
    await existing_chain.asave(update_fields=as_dict.keys())

    # create / destroy agent if needed.
    await sync_chain_agent(existing_chain, alias=chain.alias)

    # sync properties to test agent
    await Agent.objects.filter(chain=existing_chain, is_test=True).aupdate(
        name=chain.name,
        purpose=chain.description,
    )

    response = ChainPydantic.model_validate(existing_chain)
    response.alias = chain.alias
    return response


@router.delete(
    "/chains/{chain_id}",
    operation_id="delete_chain",
    response_model=DeletedItem,
    tags=["Chains"],
)
async def delete_chain(chain_id: UUID, user: AbstractUser = Depends(get_request_user)):
    query = Chain.filtered_owners(user)
    try:
        existing_chain = await query.aget(id=chain_id)
    except Chain.DoesNotExist:
        raise HTTPException(status_code=404, detail="Chain not found")
    await existing_chain.adelete()
    return DeletedItem(id=chain_id)
