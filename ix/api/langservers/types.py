from typing import List, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ix.utils.graphene.pagination import QueryPage


class LangServerImport(BaseModel):
    """Represents inputs required for importing a LangServer from a remote endpoint."""

    url: str


class RemoteRunnableConfig(BaseModel):
    name: str
    input_schema: dict
    output_schema: dict
    config_schema: dict


class LangServerConfig(BaseModel):
    name: str
    description: str
    url: str
    routes: List[RemoteRunnableConfig]


class LangServer(BaseModel):
    id: UUID
    name: str
    description: str
    url: str
    routes: List[RemoteRunnableConfig]
    headers: Dict[str, str] = Field(default_factory=dict)

    class Config:
        orm_mode = True


class LangServerCreateUpdate(BaseModel):
    name: str
    description: str
    url: str
    headers: Optional[dict] = Field(default_factory=dict)
    routes: List[RemoteRunnableConfig] = Field(default_factory=list)


class LangServerPage(QueryPage[LangServer]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[LangServer]
