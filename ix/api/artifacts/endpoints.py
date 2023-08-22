from uuid import UUID

from asgiref.sync import sync_to_async
from django.db.models import Q
from fastapi import HTTPException, APIRouter
from typing import Optional
from ix.api.artifacts.types import (
    Artifact as ArtifactPydantic,
    ArtifactCreate,
    ArtifactUpdate,
    ArtifactPage,
)
from ix.task_log.models import Artifact


router = APIRouter()
__all__ = ["router"]


@router.post("/artifacts/", response_model=ArtifactPydantic, tags=["Artifacts"])
async def create_artifact(data: ArtifactCreate):
    instance = Artifact(**data.model_dump())
    await instance.asave()
    return ArtifactPydantic.model_validate(instance)


@router.get(
    "/artifacts/{artifact_id}", response_model=ArtifactPydantic, tags=["Artifacts"]
)
async def get_artifact(artifact_id: str):
    try:
        artifact = await Artifact.objects.aget(pk=artifact_id)
    except Artifact.DoesNotExist:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return ArtifactPydantic.model_validate(artifact)


@router.get("/artifacts/", response_model=ArtifactPage, tags=["Artifacts"])
async def get_artifacts(
    chat_id: Optional[UUID] = None,
    search: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
):
    query = (
        Artifact.objects.filter(Q(name__icontains=search) | Q(key__icontains=search))
        if search
        else Artifact.objects.all()
    )
    if chat_id:
        query = query.filter(task__leading_chats__id=chat_id)

    # punting on async implementation of pagination until later
    return await sync_to_async(ArtifactPage.paginate)(
        output_model=ArtifactPydantic, queryset=query, limit=limit, offset=offset
    )


@router.put(
    "/artifacts/{artifact_id}", response_model=ArtifactPydantic, tags=["Artifacts"]
)
async def update_artifact(artifact_id: str, data: ArtifactUpdate):
    try:
        instance = await Artifact.objects.aget(pk=artifact_id)
    except Artifact.DoesNotExist:
        raise HTTPException(status_code=404, detail="Artifact not found")
    for attr, value in data.model_dump().items():
        setattr(instance, attr, value)
    await instance.asave()
    return ArtifactPydantic.model_validate(instance)
