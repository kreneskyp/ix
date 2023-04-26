from typing import Any, Dict

from ix.agents.exceptions import AuthRequired
from ix.agents.process import AgentProcess
from ix.task_log.models import TaskLogMessage


class GenerativeAgentProcess(AgentProcess):
    # Generative agents respond to input from users (or other agents) to
    # produce a set of artifacts. They do not generate anything autonomously.
    ALLOWS_AUTONOMOUS = False

    PROMPT = """"""
    OUTPUT_FORMAT = """"""

    def handle_response(self, execute: bool, response: Dict[str, Any]):
        artifact_msg = self.save_artifacts(response)
        raise AuthRequired(artifact_msg)

    def save_artifacts(self, response: Dict[str, Any]) -> TaskLogMessage:
        raise NotImplementedError
