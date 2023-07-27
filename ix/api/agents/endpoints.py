from django.db.models import Q
from fastapi import HTTPException, APIRouter
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from ix.agents.models import Agent
from ix.api.chains.endpoints import DeletedItem
from ix.api.agents.types import Agent as AgentPydantic

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
async def create_agent(agent: AgentCreateUpdate):
    agent_obj = Agent(**agent.dict())
    await agent_obj.asave()
    return AgentPydantic.from_orm(agent_obj)


@router.get("/agents/{agent_id}", response_model=AgentPydantic, tags=["Agents"])
async def get_agent(agent_id: str):
    try:
        agent = await Agent.objects.aget(pk=agent_id)
    except Agent.DoesNotExist:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentPydantic.from_orm(agent)


@router.get("/agents/", response_model=List[AgentPydantic], tags=["Agents"])
async def get_agents(search: Optional[str] = None):
    query = (
        Agent.objects.filter(Q(name__icontains=search) | Q(alias__icontains=search))
        if search
        else Agent.objects.all()
    )
    return [AgentPydantic.from_orm(agent) async for agent in query]


@router.put("/agents/{agent_id}", response_model=AgentPydantic, tags=["Agents"])
async def update_agent(agent_id: str, agent: AgentCreateUpdate):
    try:
        agent_obj = await Agent.objects.aget(pk=agent_id)
    except Agent.DoesNotExist:
        raise HTTPException(status_code=404, detail="Agent not found")
    for attr, value in agent.dict().items():
        setattr(agent_obj, attr, value)
    await agent_obj.asave()
    return agent_obj


@router.delete("/agents/{agent_id}", response_model=DeletedItem, tags=["Agents"])
async def delete_agent(agent_id: str):
    try:
        agent = await Agent.objects.aget(pk=agent_id)
    except Agent.DoesNotExist:
        raise HTTPException(status_code=404, detail="Agent not found")
    await agent.adelete()
    return DeletedItem(id=agent_id)
