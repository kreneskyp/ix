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
    memory_key: str = "related_artifacts"

    session_id: str
    supports_session: bool = True
    supported_scopes: set = {"chat"}

    @property
    def memory_variables(self) -> List[str]:
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load related artifacts into memory"""
        logger.debug(
            f"ArtifactMemory.load_memory_variables input_key={self.input_key} inputs={inputs}"
        )

        # split session id back into chat_id
        chat_id = self.session_id.split("_")[-1]

        # search for artifacts
        text = ""
        artifact_keys = inputs.get(self.input_key, None)
        if artifact_keys:
            artifacts = Artifact.objects.filter(
                (Q(key__in=artifact_keys) | Q(name__in=artifact_keys)),
                (
                    Q(task__leading_chats__id=chat_id)
                    | Q(task__parent__leading_chats__id=chat_id)
                ),
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
        return {self.memory_key: text}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        No-op for now. May move artifact saving here in the future. Artifacts
        are currently saved by SaveArtifact chain.
        """
        pass

    def clear(self) -> None:
        pass
