import base64
import json
import logging
from io import BytesIO
from typing import Any, Optional, List, Union, AsyncIterator
from uuid import UUID
import aiofiles
from PIL.Image import Image

from langchain.schema.runnable import RunnableSerializable, RunnableConfig, Runnable
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.utils import Input, Output
from pydantic import BaseModel

from ix.chains.callbacks import IxHandler
from ix.commands.filesystem import write_to_file, get_work_dir
from ix.runnable.base import StreamableTransform
from ix.runnable.dalle import DalleSizes
from ix.task_log.models import Artifact, TaskLogMessage
from ix.api.artifacts.types import Artifact as ArtifactPydantic, ArtifactContent

logger = logging.getLogger(__name__)
ArtifactID = str | UUID


class LoadArtifacts(
    RunnableSerializable[Union[ArtifactID, List[ArtifactID]], List[ArtifactContent]]
):
    """Output key for loaded memories. Must match the key in the memory component."""

    def invoke(
        self,
        input: ArtifactID | List[ArtifactID],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> List[ArtifactPydantic]:
        if not isinstance(input, list):
            artifact_ids = [input]
        else:
            artifact_ids = input
        artifacts = Artifact.objects.filter(id__in=artifact_ids)
        return [ArtifactPydantic.model_validate(artifact) for artifact in artifacts]

    async def ainvoke(
        self,
        input: ArtifactID | List[ArtifactID],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> List[ArtifactPydantic]:
        if not isinstance(input, list):
            artifact_ids = [input]
        else:
            artifact_ids = input
        artifacts = Artifact.objects.filter(id__in=artifact_ids)

        # read file
        output = []
        async for artifact in artifacts:
            # read the file
            output.append(
                ArtifactPydantic(
                    id=artifact.id,
                    task_id=artifact.task_id,
                    key=artifact.key,
                    name=artifact.name,
                    description=artifact.description,
                    artifact_type=artifact.artifact_type,
                    storage=artifact.storage,
                    created_at=artifact.created_at,
                )
            )

        return output


class ArtifactMeta(BaseModel):
    type: Optional[str] = None
    key: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    storage_backend: Optional[str] = None
    storage_id: Optional[str] = None
    data: Optional[str] = None


class SaveArtifact(Runnable[ArtifactMeta, ArtifactPydantic], BaseModel):
    type: Optional[str] = None
    key: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    storage_backend: Optional[str] = "filesystem"
    storage_id: Optional[str] = None

    def invoke(
        self,
        input: ArtifactMeta,
        config: Optional[RunnableConfig] = None,
    ) -> ArtifactPydantic:
        artifact = Artifact.objects.create(
            task_id=self.context.task_id,
            key=input.key,
            name=input.name,
            description=input.description,
            artifact_type=input["type"],
            storage={
                "backend": input.storage_backend,
                "id": input.storage_id,
            },
        )

        # no new output, pass through all inputs
        return ArtifactPydantic.model_validate(artifact)

    async def ainvoke(
        self,
        input: ArtifactMeta,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> ArtifactPydantic:
        ix_handler = IxHandler.from_config(config)

        if isinstance(input, dict):
            input = ArtifactMeta(**input)

        # merge settings with input, input takes precedence
        artifact_kwargs = self.model_dump(
            include={
                "type",
                "key",
                "name",
                "description",
                "storage_backend",
                "storage_id",
                "storage_id",
            }
        )
        artifact_kwargs.update(
            {
                k: v
                for k, v in input.model_dump(exclude=["data"]).items()
                if v is not None
            }
        )
        artifact_kwargs["artifact_type"] = artifact_kwargs.pop("type")
        storage = {
            "backend": artifact_kwargs.pop("storage_backend"),
            "id": artifact_kwargs.pop("storage_id"),
        }

        # save artifact meta to database
        artifact = await Artifact.objects.acreate(
            **artifact_kwargs,
            task=ix_handler.task,
            storage=storage,
        )

        # write to storage (i.e. file, database, or a cache)
        content = input.data
        if storage["backend"] == "filesystem":
            file_path = artifact.storage["id"]
            logger.debug(f"writing content to file file_path={file_path} {content}")
            if not isinstance(content, str):
                content = json.dumps(content)
            write_to_file(file_path, content)

        # send message to log
        await TaskLogMessage.objects.acreate(
            role="ASSISTANT",
            task=ix_handler.task,
            agent=ix_handler.agent,
            parent=ix_handler.parent_think_msg,
            content={
                "type": "ARTIFACT",
                "artifact_type": artifact.artifact_type,
                "artifact_id": str(artifact.id),
                "storage": artifact.storage,
                "description": artifact.description,
                "data": content,
            },
        )

        # no new output, pass through all inputs
        return ArtifactPydantic.model_validate(artifact)


class LoadFile(StreamableTransform, RunnableSerializable[str, bytes]):
    """Load a file from the filesystem and stream its contents as bytes using aiofiles."""

    def invoke(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Output:
        with open(input, "rb") as file:
            file_contents = file.read()
        return file_contents

    async def ainvoke(
        self,
        input: str,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> bytes:
        # Asynchronous file loading using aiofiles
        async with aiofiles.open(get_work_dir() / input, "rb") as file:
            file_contents = await file.read()
        return file_contents

    async def atransform(
        self,
        input: AsyncIterator[Input],
        config: Optional[RunnableConfig] = None,
        **kwargs: Optional[Any],
    ) -> AsyncIterator[Output]:
        async for file_path in input:
            async with aiofiles.open(get_work_dir() / file_path, "rb") as file:
                file_contents = await file.read()
            yield file_contents


BASE64_JPG_URI = "data:image/jpeg;base64,"


class EncodeImage(StreamableTransform, RunnableSerializable[bytes, str]):
    """Transform an image into a base64 string."""

    size: Optional[DalleSizes] = None

    def invoke(
        self,
        input: bytes,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> str:
        return f"{BASE64_JPG_URI}{self.encode_bytes(input)}"

    async def ainvoke(
        self,
        input: bytes,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> str:
        return f"{BASE64_JPG_URI}{self.encode_bytes(input)}"

    async def atransform(
        self,
        input: AsyncIterator[Input],
        config: Optional[RunnableConfig] = None,
        **kwargs: Optional[Any],
    ) -> AsyncIterator[Output]:
        if self.size:
            # Aggregate chunks into a single byte string for resizing
            input_bytes = b"".join([chunk for chunk in input])
            yield str(BASE64_JPG_URI)
            yield self.encode_bytes(input_bytes)
        else:
            # Stream encode individual chunks
            yield str(BASE64_JPG_URI)
            async for chunk in input:
                encoded_chunk = self.encode_bytes(chunk)
                yield encoded_chunk

    def resize_image(self, input: bytes) -> bytes:
        """
        Resize the image data.

        Args:
            input (bytes): The input image data in bytes.

        Returns:
            bytes: The resized image data in bytes.
        """
        image = Image.open(BytesIO(input))
        image = image.resize(self.size, Image.ANTIALIAS)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return buffered.getvalue()

    def encode_bytes(self, input: bytes) -> str:
        """
        Encode the image as a base64 string.

        Args:
            input (bytes): The input image data in bytes.

        Returns:
            str: The base64-encoded image as a string.
        """
        return base64.b64encode(input).decode("utf-8")


def get_load_image_artifact() -> Runnable:
    """
    Sequence that loads a single artifact and then encodes it as a base64 string.
    """
    return (
        LoadArtifacts()
        | RunnableLambda(lambda x: x[0].storage["id"])
        | LoadFile()
        | EncodeImage()
    )
