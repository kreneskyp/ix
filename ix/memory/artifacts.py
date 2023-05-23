from typing import Dict, Any, List

from langchain.schema import BaseMemory

from ix.task_log.models import Artifact


class ArtifactMemory(BaseMemory):
    """
    A memory implementation that loads artifacts into the context
    """

    save_artifact: bool = False
    load_artifact: bool = False

    # read
    variable: str = "related_artifacts"
    scope: str = None

    # write
    # TODO

    @property
    def memory_variables(self) -> List[str]:
        return ["related_artifacts"]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load related artifacts into memory"""

        # search for artifacts

        # TODO: limit scope of artifact query
        # TODO: add support for LLM search
        # TODO: add support for similarity search
        referenced_keys = inputs.get("referenced_artifact_keys", None)
        if referenced_keys:
            artifacts = Artifact.objects.filter(key__in=referenced_keys)

            # format each artifact
            artifact_strs = []
            for artifact in artifacts:
                artifact_strs.append(artifact.as_memory_text())
            artifact_prompt = "\n\n".join(artifact_strs)
            text = f"REFERENCED ARTIFACTS:\n\n {artifact_prompt}"
        else:
            text = ""

        # return formatted artifacts
        return {self.variable: text}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save artifacts from step"""
        # TODO: move SaveArtifact logic here
        pass

    def clear(self) -> None:
        pass
