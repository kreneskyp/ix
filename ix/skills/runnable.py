from typing import Optional

from asgiref.sync import sync_to_async
from langchain.schema.runnable import (
    RunnableSerializable,
    RunnableConfig,
)
from langchain.schema.runnable.utils import Input, Output
from pydantic import UUID4

from ix.skills.models import Skill
from ix.skills.types import Skill as SkillPydantic
from ix.skills.utils import run_code_with_repl


class LoadSkill(RunnableSerializable[Input, SkillPydantic]):
    """Get a skill from the IX skill registry"""

    skill_id: UUID4

    def invoke(
        self, input: Input, config: Optional[RunnableConfig] = None, **kwargs
    ) -> SkillPydantic:
        instance = Skill.objects.get(pk=self.skill_id)
        return SkillPydantic.model_validate(instance)

    async def ainvoke(
        self, input: Input, config: Optional[RunnableConfig] = None, **kwargs
    ) -> SkillPydantic:
        instance = await Skill.objects.aget(pk=self.skill_id)
        return SkillPydantic.model_validate(instance)


class RunSkill(RunnableSerializable[Input, Output]):
    """Run a skill"""

    skill: SkillPydantic

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        orm_mode = True
        exclude = {"skill"}

    def get_input_schema(self, config: Optional[RunnableConfig] = None):
        return self.skill.input_type

    def invoke(
        self, input: Input, config: Optional[RunnableConfig] = None, **kwargs
    ) -> Output:
        return run_code_with_repl(self.skill.code, self.skill.func_name, input)

    async def ainvoke(
        self, input: Input, config: Optional[RunnableConfig] = None, **kwargs
    ) -> Output:
        repl = sync_to_async(run_code_with_repl)
        return await repl(self.skill.code, self.skill.func_name, input)

    @classmethod
    def from_db(cls, skill_id: UUID4) -> "RunSkill":
        instance = Skill.objects.get(pk=skill_id)
        skill = SkillPydantic.model_validate(instance)
        return cls(skill=skill)
