from typing import Any, Dict

from ix.agents.process import AgentProcess


# class PlanningAgent(AgentProcess):
class GenerativeAgentProcess(AgentProcess):
    # Generative agents respond to input from users (or other agents) to
    # produce a set of artifacts. They do not generate anything autonomously.
    ALLOWS_AUTONOMOUS = False

    PROMPT = """"""
    OUTPUT_FORMAT = """"""

    def handle_response(self, execute: bool, response: Dict[str, Any]):
        self.save_artifacts(response)

    def save_artifacts(self, obj):
        pass
        # write to db for precise search
        # write to vector storage for similarity search
