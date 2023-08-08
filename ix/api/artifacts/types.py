from pydantic import BaseModel, UUID4
from typing import Dict, Any, Optional
from datetime import datetime


class ArtifactBase(BaseModel):
    task_id: UUID4
    key: str
    artifact_type: str
    name: str
    description: str
    storage: Dict[str, Any]


class ArtifactCreate(ArtifactBase):
    pass


class ArtifactUpdate(ArtifactBase):
    task_id: Optional[UUID4] = None
    key: Optional[str] = None
    artifact_type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    storage: Optional[Dict[str, Any]] = None


class Artifact(ArtifactBase):
    id: UUID4
    created_at: datetime

    class Config:
        orm_mode = True
