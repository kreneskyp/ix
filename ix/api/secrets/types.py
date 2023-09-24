from typing import Optional, List, Dict, Any

from pydantic import BaseModel, UUID4, root_validator

from ix.utils.graphene.pagination import QueryPage


class Secret(BaseModel):
    id: UUID4
    user_id: int
    type: Optional[str] = None
    name: str = "default"
    path: str

    class Config:
        orm_mode = True

    @root_validator
    def validate_secret(cls, values):
        """
        Path should only show information relative to the user's root.
        Hide full path from API.
        """
        pk = values.get("id")
        type_ = values.get("type")
        values["path"] = f"{type_}/{pk}"
        return values


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
