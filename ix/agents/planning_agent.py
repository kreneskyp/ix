from typing import Any, Dict

from ix.agents.generative_agent import GenerativeAgentProcess
from ix.chat.models import Artifact
from ix.task_log.models import TaskLogMessage, Plan, PlanSteps


class PlanningAgent(GenerativeAgentProcess):
    INSTRUCTION_CLAUSE = """

        ARTIFACTS: Artifacts represent the results or consequences of executing a command or action.
        They can be new objects created (e.g., code components, data, files) or changes to the system
        or environment state (e.g., modified settings, enabled features, activated services).

        Generate a PLAN:
            - use the available COMMANDS to build a PLAN to complete the GOALS.
            - include a list of required ARTIFACTS for each COMMAND
            - include a list of ARTIFACTS the COMMAND produces.
            - the plan's `goal_artifacts` should fulfill the goal
            - every COMMAND must produce at least one ARTIFACT representing a new object or state.
            - for each command consider how it will complete the GOALS.
            - If you cannot determine a plan or an input, respond using the QUESTION_FORMAT.
            - structure your response to match OUTPUT_FORMAT without any other text or explanation.
            - output must include markers, begin with ###START### and end with ###END### .
        """

    OUTPUT_FORMAT = """
    ###START###
    {
        "output_format": "PLAN"
        "name": "name of plan",
        "description": "one or two sentences describing what the plan does.
        "commands": [
            {
                name: "step_name",
                "command": {
                    "name": "command name",
                    "args":{
                        "arg name": "value"
                    }
                }
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
            f"""{commands_clause}\n\n"""
            f"""OUTPUT_FORMAT:\n{self.OUTPUT_FORMAT}"""
            f"""INSTRUCTIONS:\n{self.INSTRUCTION_CLAUSE}\n\n"""
        )

    def save_artifacts(self, response: Dict[str, Any]):
        """
        Save the PLAN as an artifact in the database
        """

        plan = Plan.objects.create(
            name=response["name"],
            description=response["description"],
            creator=self.task,
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
