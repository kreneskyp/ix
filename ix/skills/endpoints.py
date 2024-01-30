import logging
from uuid import UUID

from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends, HTTPException

from ix.api.chains.endpoints import DeletedItem
from ix.skills.models import Skill
from ix.skills.types import (
    Skill as SkillPydantic,
    SkillPage,
    EditSkill,
)
from ix.ix_users.models import User
from ix.api.auth import get_request_user

logger = logging.getLogger(__name__)
router = APIRouter()


# Skill Endpoints
@router.post(
    "/skills/",
    operation_id="create_skill",
    response_model=SkillPydantic,
    tags=["Skills"],
)
async def create_skill(skill: EditSkill, user: User = Depends(get_request_user)):
    skill_obj = await Skill.objects.acreate(user_id=user.id, **skill.model_dump())
    return SkillPydantic.model_validate(skill_obj)


@router.get(
    "/skills/{skill_id}",
    operation_id="get_skill",
    response_model=SkillPydantic,
    tags=["Skills"],
)
async def get_skill(skill_id: UUID, user: User = Depends(get_request_user)):
    try:
        skill = await Skill.filtered_owners(user).aget(pk=skill_id)
    except Skill.DoesNotExist:
        raise HTTPException(status_code=404, detail="Skill not found")
    return SkillPydantic.model_validate(skill)


@router.get(
    "/skills/", operation_id="get_skills", response_model=SkillPage, tags=["Skills"]
)
async def get_skills(
    limit: int = 10,
    offset: int = 0,
    tags: list[str] = None,
    user: User = Depends(get_request_user),
):
    query = Skill.filtered_owners(user)
    if tags:
        query = query.filter(tags__overlap=tags)

    # punting on async implementation of pagination until later
    return await sync_to_async(SkillPage.paginate)(
        output_model=SkillPydantic, queryset=query, limit=limit, offset=offset
    )


@router.put(
    "/skills/{skill_id}",
    operation_id="update_skill",
    response_model=SkillPydantic,
    tags=["Skills"],
)
async def update_skill(
    skill_id: UUID, skill_data: EditSkill, user: User = Depends(get_request_user)
):
    try:
        skill_obj = await Skill.filtered_owners(user).aget(pk=skill_id)
    except Skill.DoesNotExist:
        raise HTTPException(status_code=404, detail="Skill not found")

    for attr, value in skill_data.model_dump().items():
        setattr(skill_obj, attr, value)
    await skill_obj.asave()
    return SkillPydantic.model_validate(skill_obj)


@router.delete("/skills/{skill_id}", operation_id="delete_skill", tags=["Skills"])
async def delete_skill(skill_id: UUID, user: User = Depends(get_request_user)):
    try:
        skill = await Skill.filtered_owners(user).aget(pk=skill_id)
    except Skill.DoesNotExist:
        raise HTTPException(status_code=404, detail="Skill not found")

    await skill.adelete()
    return DeletedItem(id=str(skill_id))
