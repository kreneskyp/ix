from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

import logging

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
