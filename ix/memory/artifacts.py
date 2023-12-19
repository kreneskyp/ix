import logging
import concurrent.futures
from typing import Dict, Any, List

from django.db.models import Q
from langchain.schema import BaseMemory

from ix.task_log.models import Artifact
from ix.utils.asyncio import run_coroutine_in_new_loop

logger = logging.getLogger(__name__)


class ArtifactMemory(BaseMemory):
    """
    A memory implementation that loads artifacts into the context
    """

    save_artifact: bool = False
    load_artifact: bool = False

    # read
    input_key: str = "artifact_ids"
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
        artifact_ids = inputs.get(self.input_key, None)
        if artifact_ids:
            id_clauses = Q(pk__in=artifact_ids)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    run_coroutine_in_new_loop, self.get_artifacts(chat_id, id_clauses)
                )
                text = future.result()

        # return formatted artifacts
        return {self.memory_key: text}

    async def get_artifacts(self, chat_id, id_clauses) -> None:
        text = ""
        artifacts = Artifact.objects.filter(
            id_clauses,
            (
                Q(task__leading_chats__id=chat_id)
                | Q(task__parent__leading_chats__id=chat_id)
            ),
        ).order_by("-created_at")

        artifacts = [artifact async for artifact in artifacts]
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

        return text

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        No-op for now. May move artifact saving here in the future. Artifacts
        are currently saved by SaveArtifact chain.
        """
        pass

    def clear(self) -> None:
        pass
