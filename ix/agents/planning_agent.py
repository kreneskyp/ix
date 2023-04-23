from typing import Any, Dict

from ix.agents.generative_agent import GenerativeAgentProcess
from ix.chat.models import Artifact
from ix.task_log.models import TaskLogMessage, Plan, PlanSteps


class PlanningAgent(GenerativeAgentProcess):
    INSTRUCTION_CLAUSE = (
        """
        Generate a PLAN:
            - use the available COMMANDS to build a PLAN for the GOALS.
            - include a list of PREREQUISITES for each COMMAND.
            - include a list of ARTIFACTS to store the result of a COMMAND.
            - every COMMAND must produce at least one ARTIFACT representing a new object or state.
            - for each command consider how it will complete the GOALS.
            - if you cannot determine a plan respond using the QUESTION_FORMAT
            - if you cannot determine an input respond using the QUESTION_FORMAT
            - structure your response to match OUTPUT_FORMAT without any other text or explanation.
            - OUTPUT_FORMAT must begin with ###START### and end with ###END###.
        """
    )

    OUTPUT_FORMAT = """
    ###START###
    {
        "output_format": "PLAN"
        "name": "name of plan",
        "description": "one or two sentences describing what the plan does.
        "commands": [
            {
                name: "step_name",
                reason: "short description of why this step is needed",
                "command": {
                    "name": "command name",
                    "args":{
                        "arg name": "value"
                    }
                }
                completes_goal: "goal_name"
                requires_artifacts: ["artifact_name"]
                produces_artifacts: ["artifact_name"]
            }
        ]
        "goal_artifacts": ["artifact_name"]
    }
    ###END###
    """

    def build_base_prompt(self):
        agent = self.agent
        commands_clause = self.command_registry.command_prompt()
        return (
            f"""You are {agent.name}, {agent.purpose}\n\n"""
            f"""INSTRUCTIONS:\n{self.INSTRUCTION_CLAUSE}\n\n"""
            f"""{commands_clause}\n\n"""
            f"""OUTPUT_FORMAT:\n{self.OUTPUT_FORMAT}"""
        )

    def save_artifacts(self, response: Dict[str, Any]):
        """
        Save the PLAN as an artifact in the database
        """

        plan = Plan.objects.create(
            name=response["name"],
            description=response["description"],
        )

        for command in response["commands"]:
            PlanSteps.objects.create(plan=plan, details=command)

        artifact = Artifact.objects.create(
            task=self.task,
            key="plan",
            name=response["name"],
            description=response["description"],
            artifact_type="PLAN",
            reference={"plan_id": str(plan.id)},
        )

        TaskLogMessage.objects.create(
            role="assistant",
            task=self.task,
            agent=self.agent,
            content={
                "type": "ARTIFACT",
                "name": response["name"],
                "artifact_type": "PLAN",
                "artifact_id": str(artifact.id),
                "description": response["description"],
                "steps": response["commands"],
            },
        )
