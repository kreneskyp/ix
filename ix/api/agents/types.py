from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field

import logging

from ix.utils.graphene.pagination import QueryPage

logger = logging.getLogger(__name__)


class Agent(BaseModel):
    id: UUID
    name: str
    alias: str
    purpose: str
    chain_id: UUID
    model: str
    created_at: datetime
    config: dict = Field(default_factory=dict)

    class Config:
        orm_mode = True


class AgentPage(QueryPage[Agent]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[Agent]
