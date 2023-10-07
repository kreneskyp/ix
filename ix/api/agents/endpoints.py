from asgiref.sync import sync_to_async
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from ix.agents.models import Agent
from ix.api.auth import get_request_user
from ix.api.chains.endpoints import DeletedItem
from ix.api.agents.types import Agent as AgentPydantic, AgentPage

__all__ = ["router", "AgentCreateUpdate"]


router = APIRouter()


class AgentCreateUpdate(BaseModel):
    name: str
    alias: str
    purpose: str
    chain_id: UUID
    model: str = "gpt-4"
    config: dict = {}


@router.post("/agents/", response_model=AgentPydantic, tags=["Agents"])
async def create_agent(
    agent: AgentCreateUpdate, user: AbstractUser = Depends(get_request_user)
):
    agent_obj = Agent(user=user, **agent.dict())
    await agent_obj.asave()
    return AgentPydantic.from_orm(agent_obj)


@router.get("/agents/{agent_id}", response_model=AgentPydantic, tags=["Agents"])
async def get_agent(agent_id: str, user: AbstractUser = Depends(get_request_user)):
    try:
        query = Agent.objects.filter(pk=agent_id)
        agent = await Agent.filter_owners(user, query).aget()
    except Agent.DoesNotExist:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentPydantic.from_orm(agent)


@router.get("/agents/", response_model=AgentPage, tags=["Agents"])
async def get_agents(
    search: Optional[str] = None,
    chat_id: Optional[UUID] = None,
    limit: int = 10,
    offset: int = 0,
    user: AbstractUser = Depends(get_request_user),
):
    query = Agent.objects.filter(is_test=False).order_by("alias")
    query = Agent.filter_owners(user, query)
    if chat_id:
        query = query.filter(chats__id=chat_id)
    if search:
        query = query.filter(Q(name__icontains=search) | Q(alias__icontains=search))

    # punting on async implementation of pagination until later
    return await sync_to_async(AgentPage.paginate)(
        output_model=AgentPydantic, queryset=query, limit=limit, offset=offset
    )


@router.put("/agents/{agent_id}", response_model=AgentPydantic, tags=["Agents"])
async def update_agent(
    agent_id: str,
    agent: AgentCreateUpdate,
    user: AbstractUser = Depends(get_request_user),
):
    try:
        query = Agent.objects.filter(pk=agent_id)
        agent_obj = await Agent.filter_owners(user, query).aget()
    except Agent.DoesNotExist:
        raise HTTPException(status_code=404, detail="Agent not found")
    for attr, value in agent.dict().items():
        setattr(agent_obj, attr, value)
    await agent_obj.asave()
    return agent_obj


@router.delete("/agents/{agent_id}", response_model=DeletedItem, tags=["Agents"])
async def delete_agent(agent_id: str, user: AbstractUser = Depends(get_request_user)):
    try:
        query = Agent.objects.filter(pk=agent_id)
        agent = await Agent.filter_owners(user, query).aget()
    except Agent.DoesNotExist:
        raise HTTPException(status_code=404, detail="Agent not found")
    await agent.adelete()
    return DeletedItem(id=agent_id)
