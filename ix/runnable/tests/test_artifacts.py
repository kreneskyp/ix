import base64
import pytest
import pytest_asyncio
from langchain.schema.runnable import RunnableConfig

from ix.chains.loaders.context import IxContext
from ix.runnable.artifacts import (
    SaveArtifact,
    ArtifactMeta,
    LoadArtifacts,
    LoadFile,
    EncodeImage,
    get_load_image_artifact,
    BASE64_JPG_URI,
)
from ix.task_log.models import Artifact


@pytest.mark.django_db
class TestSaveArtifact:
    async def test_invoke(self, aix_handler, aix_context: IxContext, mock_filesystem):
        """Verify artifact can be saved

        - file is written
        - artifact is created in db
        - message is logged
        """

        save_artifact = SaveArtifact(
            type="file",
            key="test_artifact",
            name="test artifact",
            description="this is a test artifact",
            storage_backend="filesystem",
            storage_id="test_artifact.txt",
        )

        inputs = ArtifactMeta(
            data="this is mock content",
        )

        result = await save_artifact.ainvoke(
            input=inputs, config=RunnableConfig(callbacks=[aix_handler])
        )

        # assert returned object
        assert str(result.task_id) == aix_context.task_id
        assert result.key == "test_artifact"
        assert result.name == "test artifact"
        assert result.description == "this is a test artifact"
        assert result.storage["backend"] == "filesystem"
        assert result.storage["id"] == "test_artifact.txt"

        # assert object in db
        artifact = await Artifact.objects.aget(id=result.id)
        assert str(artifact.task_id) == aix_context.task_id
        assert artifact.key == "test_artifact"
        assert artifact.name == "test artifact"
        assert artifact.description == "this is a test artifact"
        assert artifact.storage["backend"] == "filesystem"
        assert artifact.storage["id"] == "test_artifact.txt"

        # verify file was written
        file = mock_filesystem.workdir / "test_artifact.txt"
        assert file.exists()
        with open(file) as f:
            assert f.read() == "this is mock content"

    async def test_inputs_vs_config(
        self, aix_handler, aix_context: IxContext, mock_filesystem
    ):
        """Verify that other metadata can be set via input or config"""
        save_artifact = SaveArtifact(
            type="file",
            key="test_artifact",
            name="test artifact",
            description="this is a test artifact",
            storage_backend="filesystem",
            storage_id="test_artifact.txt",
        )

        inputs = ArtifactMeta(
            data="this is mock content",
            key="test_artifact2",
            name="test artifact2",
            description="this is a test artifact2",
            storage_backend="filesystem",
            storage_id="test_artifact2.txt",
        )

        result = await save_artifact.ainvoke(
            input=inputs, config=RunnableConfig(callbacks=[aix_handler])
        )

        # assert returned object
        assert str(result.task_id) == aix_context.task_id
        assert result.key == "test_artifact2"
        assert result.name == "test artifact2"
        assert result.description == "this is a test artifact2"
        assert result.storage["backend"] == "filesystem"
        assert result.storage["id"] == "test_artifact2.txt"


@pytest_asyncio.fixture()
async def artifact(aix_context: IxContext, mock_filesystem):
    artifact = await Artifact.objects.acreate(
        task_id=aix_context.task_id,
        key="test_artifact",
        name="test artifact",
        description="this is a test artifact",
        artifact_type="file",
        storage={
            "backend": "filesystem",
            "id": "test_artifact.txt",
        },
    )
    write_to_file = mock_filesystem.write_file
    write_to_file("test_artifact.txt", "this is mock content")
    yield artifact


@pytest.mark.django_db
class TestLoadArtifact:
    async def test_single_artifact(
        self, aix_context: IxContext, mock_filesystem, artifact
    ):
        # create runnable
        load_artifact = LoadArtifacts()

        # invoke runnable
        result = await load_artifact.ainvoke(
            input=artifact.id,
        )

        # assert returned object
        assert isinstance(result, list)
        assert len(result) == 1
        artifact = result[0]
        assert artifact.key == "test_artifact"
        assert artifact.name == "test artifact"
        assert artifact.description == "this is a test artifact"
        assert artifact.storage["backend"] == "filesystem"
        assert artifact.storage["id"] == "test_artifact.txt"

    async def test_multiple_artifacts(self, aix_context: IxContext, mock_filesystem):
        # create artifact
        artifact1 = await Artifact.objects.acreate(
            task_id=aix_context.task_id,
            key="test_artifact1",
            name="test artifact1",
            description="this is a test artifact1",
            artifact_type="file",
            storage={
                "backend": "filesystem",
                "id": "test_artifact1.txt",
            },
        )
        artifact2 = await Artifact.objects.acreate(
            task_id=aix_context.task_id,
            key="test_artifact2",
            name="test artifact2",
            description="this is a test artifact2",
            artifact_type="file",
            storage={
                "backend": "filesystem",
                "id": "test_artifact2.txt",
            },
        )

        # create files
        write_to_file = mock_filesystem.write_file
        write_to_file("test_artifact1.txt", "this is mock content1??")
        write_to_file("test_artifact2.txt", "this is mock content2")

        # create runnable
        load_artifact = LoadArtifacts()

        # invoke runnable
        result = await load_artifact.ainvoke(
            input=[artifact1.id, artifact2.id],
        )

        # assert returned object
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].key == "test_artifact1"
        assert result[1].key == "test_artifact2"


@pytest.mark.django_db
class TestLoadFile:
    async def test_ainvoke(self, aix_context: IxContext, mock_filesystem):
        path = str(mock_filesystem.fake_file("test.txt"))
        load_file = LoadFile()

        result = await load_file.ainvoke(
            input=str(path),
        )
        assert result == b"this is mock content"

    async def test_astream(self, aix_context: IxContext, mock_filesystem):
        path = str(mock_filesystem.fake_file("test.txt"))
        load_file = LoadFile()

        result = b""
        async for chunk in load_file.astream(input=path):
            result += chunk

        assert result == b"this is mock content"


@pytest.mark.django_db
class TestEncodeImage:
    """Test that EncodeImage runnable can convert images to base64"""

    async def test_ainvoke(self, aix_context: IxContext, mock_filesystem):
        # for the purposes of this test, the image is a text file. It's a
        # simple base64 encode so the file contents don't actually matter.
        path = str(mock_filesystem.fake_file("test.png"))

        load_file = LoadFile()
        encode_image = EncodeImage()

        file_bytes = await load_file.ainvoke(input=path)
        result = await encode_image.ainvoke(
            input=file_bytes,
        )
        expected_bytes = b"this is mock content"
        encoded_bytes = base64.b64encode(expected_bytes).decode("utf-8")
        assert result == f"{BASE64_JPG_URI}{encoded_bytes}"

    async def test_astream(self, aix_context: IxContext, mock_filesystem):
        # for the purposes of this test, the image is a text file. It's a
        # simple base64 encode so the file contents don't actually matter.
        path = str(mock_filesystem.fake_file("test.png"))

        load_file = LoadFile()
        encode_image = EncodeImage()

        file_bytes = await load_file.ainvoke(input=path)
        result = ""
        async for chunk in encode_image.astream(input=file_bytes):
            result += chunk
        expected_bytes = b"this is mock content"
        encoded_bytes = base64.b64encode(expected_bytes).decode("utf-8")
        assert result == f"{BASE64_JPG_URI}{encoded_bytes}"


@pytest.mark.django_db
class TestLoadEncode:
    async def test_ainvoke(self, artifact):
        get_image = get_load_image_artifact()
        result = await get_image.ainvoke(
            input=str(artifact.id),
        )
        expected_bytes = b"this is mock content"
        encoded_bytes = base64.b64encode(expected_bytes).decode("utf-8")
        assert result == f"{BASE64_JPG_URI}{encoded_bytes}"

    async def test_astream(self, aix_context: IxContext, mock_filesystem, artifact):
        get_image = get_load_image_artifact()

        result = ""
        async for chunk in get_image.astream(input=str(artifact.id)):
            result += chunk
        expected_bytes = b"this is mock content"
        encoded_bytes = base64.b64encode(expected_bytes).decode("utf-8")
        assert result == f"{BASE64_JPG_URI}{encoded_bytes}"
