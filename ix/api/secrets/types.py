from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, UUID4
from ix.utils.graphene.pagination import QueryPage


class SecretTypeBase(BaseModel):
    name: str
    fields_schema: Dict[str, Any]


class SecretTypeEdit(SecretTypeBase):
    pass


class SecretType(SecretTypeBase):
    id: UUID
    user_id: Optional[int]
    group_id: Optional[int]

    class Config:
        from_attributes = True


class SecretTypePage(QueryPage[SecretType]):
    objects: List[SecretType]


class Secret(BaseModel):
    id: UUID4
    user_id: Optional[int] = None
    group_id: Optional[int] = None
    type_id: UUID
    name: str = "default"
    path: str

    class Config:
        from_attributes = True


class CreateSecret(BaseModel):
    type_id: Optional[UUID] = None
    type_key: Optional[str] = None
    name: Optional[str] = "default"
    value: Dict[str, Any]


class UpdateSecret(BaseModel):
    name: str = "default"

    # secrets value are only sent for updates when they are updated
    # the values are never sent in responses so the user doesn't
    # have them to re-send with other updates.
    value: Optional[Dict[str, Any]] = None


class SecretPage(QueryPage[Secret]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[Secret]
