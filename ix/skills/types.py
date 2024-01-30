from pydantic import BaseModel, UUID4, Field, root_validator, model_validator
from typing import List, Any, Type, Optional

from ix.skills.utils import parse_skill
from ix.utils.graphene.pagination import QueryPage
from jsonschema_pydantic import jsonschema_to_pydantic


class SkillBase(BaseModel):
    name: str = Field(max_length=128)
    description: Optional[str] = None
    code: str
    tags: List[str] = Field(default_factory=list)
    func_name: Optional[str] = None
    input_schema: Optional[dict[str, Any]]

    @property
    def input_type(self) -> Type[BaseModel]:
        """Pydantic model for input schema"""
        return jsonschema_to_pydantic(self.input_schema)


def run(a: int) -> int:
    """Describe your skill here."""
    return a + 1


class EditSkill(SkillBase):
    """New or updated skill definition"""

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    def parse_code_and_set_fields(cls, values):
        code = values["code"]

        if code:
            func_name, input_schema, description = parse_skill(
                code, values.get("func_name", None), values.get("input_schema", None)
            )

            # Update values with extracted data
            values["func_name"] = func_name
            values["input_schema"] = input_schema
            values["description"] = values.get("description", description)

        return values


class Skill(SkillBase):
    """JSON and OpenAPI schemas"""

    id: UUID4 = Field(
        default=None, description="ID. Do not set when creating or updating"
    )

    class Config:
        from_attributes = True

    @property
    def input_type(self) -> Type[BaseModel]:
        return jsonschema_to_pydantic(self.input_schema)


class SkillPage(QueryPage[Skill]):
    # override objects, FastAPI isn't detecting QueryPage type
    objects: List[Skill]
