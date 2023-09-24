from uuid import UUID
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from ix.utils.graphene.pagination import QueryPage


class DataSourceBase(BaseModel):
    name: str
    description: str
    config: Dict[str, Any]
    retrieval_chain: UUID
    user_id: UUID  # Add the user_id property


class DataSourceCreate(DataSourceBase):
    id: Optional[UUID] = None


class DataSource(DataSourceBase):
    id: UUID

    class Config:
        orm_mode = True


class DataSourcePage(QueryPage[DataSource]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[DataSource]
