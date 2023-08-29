from pydantic import BaseModel, UUID4
from typing import Dict, Any, List
from datetime import datetime

from ix.utils.graphene.pagination import QueryPage


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
    pass


class Artifact(ArtifactBase):
    id: UUID4
    created_at: datetime

    class Config:
        orm_mode = True


class ArtifactPage(QueryPage[Artifact]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[Artifact]
