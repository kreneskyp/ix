from enum import Enum

from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from uuid import UUID
from datetime import datetime
from ix.api.agents.types import Agent
from ix.api.artifacts.types import Artifact
from ix.agents.models import Agent as AgentModel
from ix.utils.graphene.pagination import QueryPage


class ChatNew(BaseModel):
    name: Optional[str]
    lead_id: Optional[UUID]
    autonomous: bool = False


class Chat(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    lead_id: UUID
    autonomous: bool = False
    task_id: UUID

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, instance: Any) -> "Chat":
        return cls(
            id=instance.id,
            name=instance.name,
            created_at=instance.created_at,
            lead_id=instance.lead_id,
            task_id=instance.task_id,
        )


class ChatQueryPage(QueryPage[Chat]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[Chat]


class ChatInList(Chat):
    agents: List[Agent]

    @classmethod
    def from_orm(cls, instance: Any) -> "Chat":
        agent_query = AgentModel.objects.filter(chats__id=instance.id)
        agents = [Agent.from_orm(agent) for agent in agent_query]
        return cls(
            id=instance.id,
            name=instance.name,
            created_at=instance.created_at,
            lead_id=instance.lead_id,
            task_id=instance.task_id,
            agents=agents,
        )


class ChatUpdate(BaseModel):
    name: Optional[str]
    lead_id: Optional[UUID]
    autonomous: Optional[bool]


class ChatAgentAction(BaseModel):
    chat_id: UUID
    agent_id: Optional[UUID]


class Task(BaseModel):
    id: UUID

    class Config:
        orm_mode = True


class Plan(BaseModel):
    id: UUID

    class Config:
        orm_mode = True


class ChatGraph(BaseModel):
    chat: Chat
    lead: Agent
    agents: List[Agent]
    task: Task
    plans: List[Plan]
    artifacts: List[Artifact]


class RoleChoice(str, Enum):
    SYSTEM = "SYSTEM"
    ASSISTANT = "ASSISTANT"
    USER = "USER"


class ChatInput(BaseModel):
    """An input to a chat."""

    text: str


class ChatMessage(BaseModel):
    """A message in a chat."""

    id: UUID
    agent_id: Optional[UUID]
    created_at: datetime
    parent_id: Optional[UUID]
    role: RoleChoice
    content: Dict[str, Any]

    class Config:
        orm_mode = True


class ChatMessageQueryPage(QueryPage[ChatMessage]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[ChatMessage]
