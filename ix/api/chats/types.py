from enum import Enum

from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from uuid import UUID
from datetime import datetime
from ix.api.agents.types import Agent
from ix.api.artifacts.types import Artifact


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

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, instance: Any) -> "Chat":
        return cls(
            id=instance.id,
            name=instance.name,
            created_at=instance.created_at,
            lead_id=instance.lead_id,
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
