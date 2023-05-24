import logging
from typing import Dict, Any, List

from django.db.models import Q
from langchain.schema import BaseMemory

from ix.task_log.models import Artifact


logger = logging.getLogger(__name__)


class ArtifactMemory(BaseMemory):
    """
    A memory implementation that loads artifacts into the context
    """

    save_artifact: bool = False
    load_artifact: bool = False

    # read
    input_key: str = "artifact_keys"
    variable: str = "related_artifacts"
    scope: str = None

    # write
    # TODO

    @property
    def memory_variables(self) -> List[str]:
        return [self.variable]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load related artifacts into memory"""
        logger.debug(
            f"ArtifactMemory.load_memory_variables input_key={self.input_key} inputs={inputs}"
        )

        # search for artifacts
        # TODO: limit scope of artifact query
        # TODO: add support for LLM search
        # TODO: add support for similarity search
        text = ""
        artifact_keys = inputs.get(self.input_key, None)
        if artifact_keys:
            artifacts = Artifact.objects.filter(
                Q(key__in=artifact_keys) | Q(name__in=artifact_keys)
            ).order_by("-created_at")

            logger.debug(f"Found n={len(artifacts)} artifacts")
            if artifacts:
                # format each artifact
                # HAX: group by key to avoid duplicates, this is done here since it's
                # a lot simpler than doing it in the query. This method will still
                # query all the duplicates but only becomes an issue if there is a
                # large number of duplicates
                artifact_strs = {}
                for artifact in artifacts:
                    if artifact.key not in artifact_strs:
                        artifact_strs[artifact.key] = artifact.as_memory_text()
                artifact_prompt = "".join(artifact_strs.values())
                text = f"REFERENCED ARTIFACTS:\n{artifact_prompt}"

        # return formatted artifacts
        logger.debug(f"ArtifactMemory.load_memory_variables text={text}")
        return {self.variable: text}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save artifacts from step"""
        # TODO: move SaveArtifact logic here
        pass

    def clear(self) -> None:
        pass
