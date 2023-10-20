from typing import Optional, List, Dict, Any

from pydantic import BaseModel, UUID4

from ix.utils.graphene.pagination import QueryPage


class Secret(BaseModel):
    id: UUID4
    user_id: int
    type: Optional[str] = None
    name: str = "default"
    path: str

    class Config:
        from_attributes = True


class CreateSecret(BaseModel):
    type: str
    name: Optional[str] = "default"
    value: Dict[str, Any]


class UpdateSecret(BaseModel):
    name: str = "default"
    value: Dict[str, Any]


class SecretPage(QueryPage[Secret]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[Secret]
