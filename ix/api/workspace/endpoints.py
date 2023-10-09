import logging
from pathlib import Path

from django.conf import settings
from fastapi import APIRouter, UploadFile, File, Form

from ix.task_log.models import Artifact
from ix.api.artifacts.types import (
    Artifact as ArtifactPydantic
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload/", response_model=ArtifactPydantic)
async def upload_file(file: UploadFile = File(...), task_id: str = Form(None)):
    file_location = Path(settings.WORKSPACE_DIR) / file.filename
    with file_location.open("wb+") as buffer:
        buffer.write(file.file.read())

    artifact = await Artifact.objects.acreate(
        task_id=task_id,
        artifact_type="file",
        name=file.filename,
        key=file.filename,
        description="",
        storage={
            "type": "write_file",
            "storage_id": str(file_location),
        }
    )

    return ArtifactPydantic.from_orm(artifact)
