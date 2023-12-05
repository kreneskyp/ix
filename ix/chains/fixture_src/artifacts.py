from ix.api.components.types import NodeTypeField
from ix.chains.fixture_src.targets import FLOW_TYPES
from ix.runnable.artifacts import ArtifactMeta

ARTIFACT_MEMORY = {
    "class_path": "ix.memory.artifacts.ArtifactMemory",
    "type": "memory",
    "name": "Artifact Memory",
    "description": "Memory that retrieves artifacts from the database.",
    "fields": [
        {
            "name": "save_artifact",
            "label": "Save Artifact",
            "type": "boolean",
            "default": False,
        },
        {
            "name": "load_artifact",
            "label": "Load Artifact",
            "type": "boolean",
            "default": True,
        },
        {
            "name": "input_key",
            "type": "string",
            "default": "artifact_keys",
        },
        {
            "name": "memory_key",
            "type": "string",
            "default": "related_artifacts",
        },
    ],
}


SAVE_ARTIFACT = {
    "class_path": "ix.chains.artifacts.SaveArtifact",
    "type": "chain",
    "name": "Save Artifact",
    "description": "Saves an input as an artifact",
    "fields": [
        {
            "name": "artifact_key",
            "label": "Artifact Key",
            "type": "string",
            "required": True,
            "description": "Key of the artifact to save",
        },
        {
            "name": "artifact_name",
            "type": "string",
            "required": True,
            "description": "Name of the artifact to save",
        },
        {
            "name": "artifact_description",
            "type": "string",
            "required": True,
            "description": "Description of the artifact to save",
        },
        {
            "name": "artifact_type",
            "type": "string",
            "required": True,
            "description": "Type of the artifact to save",
        },
        {
            "name": "artifact_storage",
            "type": "string",
            "required": True,
            "description": "Storage of the artifact to save",
            "default": "write_to_file",
        },
        {
            "name": "artifact_storage_id_key",
            "label": "Storage ID Key",
            "type": "string",
            "required": True,
            "description": "key within the input containing the storage ID",
        },
        {
            "name": "content_key",
            "type": "string",
            "required": True,
            "description": "Key of the input containing the content to save",
        },
        {
            "name": "output_key",
            "type": "string",
            "required": True,
            "description": "Key that the artifact will be output to",
        },
    ],
}


RUNNABLE_SAVE_ARTIFACT_CLASS_PATH = "ix.runnable.artifacts.SaveArtifact"
RUNNABLE_SAVE_ARTIFACT = {
    "class_path": RUNNABLE_SAVE_ARTIFACT_CLASS_PATH,
    "type": "chain",
    "name": "Save Artifact",
    "description": "Saves an input as an artifact",
    "connectors": [
        {
            "key": "in",
            "label": "data",
            "type": "target",
            "source_type": FLOW_TYPES,
        }
    ],
    "fields": NodeTypeField.get_fields(
        ArtifactMeta,
        include=[
            "type",
            "key",
            "name",
            "description",
            "storage_backend",
            "storage_id",
        ],
    ),
}


RUNNABLE_LOAD_ARTIFACTS_CLASS_PATH = "ix.runnable.artifacts.LoadArtifacts"
RUNNABLE_LOAD_ARTIFACTS = {
    "class_path": RUNNABLE_LOAD_ARTIFACTS_CLASS_PATH,
    "type": "chain",
    "name": "Load Artifacts",
    "description": "Loads artifacts from the database",
    "fields": [],
    "input_fields": NodeTypeField.get_fields(
        ArtifactMeta,
        include=["artifact_ids"],
    ),
}


ARTIFACTS = [
    ARTIFACT_MEMORY,
    SAVE_ARTIFACT,
    RUNNABLE_SAVE_ARTIFACT,
    RUNNABLE_LOAD_ARTIFACTS,
]
