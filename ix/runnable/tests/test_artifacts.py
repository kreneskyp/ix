import pytest
from langchain.schema.runnable import RunnableConfig

from ix.chains.loaders.context import IxContext
from ix.runnable.artifacts import SaveArtifact, ArtifactMeta, LoadArtifacts
from ix.task_log.models import Artifact


@pytest.fixture()
def mock_filesystem(mocker, tmp_path):
    """Mock filesystem backend"""

    def write_file(path, data):
        with open(tmp_path / path, "w") as f:
            f.write(data)

    def read_file(path):
        with open(tmp_path / path) as f:
            return f.read()

    mocker.patch("ix.runnable.artifacts.write_to_file", side_effect=write_file)
    mocker.patch("ix.runnable.artifacts.read_file", side_effect=read_file)

    yield {
        "workdir": tmp_path,
        "write_file": write_file,
        "read_file": read_file,
    }


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
            context=aix_context,
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
        file = mock_filesystem["workdir"] / "test_artifact.txt"
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
            context=aix_context,
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


@pytest.mark.django_db
class TestLoadArtifact:
    async def test_single_artifact(self, aix_context: IxContext, mock_filesystem):
        # create artifact
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
        write_to_file = mock_filesystem["write_file"]
        write_to_file("test_artifact.txt", "this is mock content")

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
        assert artifact.data == "this is mock content"

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
        write_to_file = mock_filesystem["write_file"]
        write_to_file("test_artifact1.txt", "this is mock content1")
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
        assert result[0].data == "this is mock content1"
        assert result[1].data == "this is mock content2"
