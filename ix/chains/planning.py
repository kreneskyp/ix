import logging
from typing import Dict, Any, List

from langchain import LLMChain, PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from ix.agents.llm import load_llm

from langchain.chains.base import Chain

from ix.agents.callback_manager import IxCallbackManager
from ix.chat.models import Artifact
from ix.commands import CommandRegistry
from ix.task_log.models import TaskLogMessage, Plan, PlanSteps


logger = logging.getLogger(__name__)


OUTPUT_FORMAT = """
###START###
{
    "output_format": "PLAN"
    "name": "name of plan",
    "description": "one or two sentences describing what the plan does.
    "goal_artifacts": ["artifact_name"]
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
}
###END###
"""

INSTRUCTION_CLAUSE = """
You are an expert planner. You create plans that fulfill the users request.

COMMANDS:
{tools}

OUTPUT_FORMAT:
{format}

ARTIFACTS: Artifacts represent the results or consequences of executing a command or action.
They can be new objects created (e.g., code components, data, files) or changes to the system
or environment state (e.g., modified settings, enabled features, activated services).

INSTRUCTIONS TO CREATE A PLAN:
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


def load_registry(tools: list) -> CommandRegistry:
    # load instance specific tools
    tool_registry = CommandRegistry()
    for class_path in tools or []:
        tool_registry.import_commands(class_path)
    return tool_registry


class CreatePlan(LLMChain):
    """Chain to create new plans."""

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @classmethod
    def from_config(cls, config: Dict[str, Any], callback_manager: IxCallbackManager):
        logger.debug(f"Loading PlanningCreateChain config={config}")
        config["llm"] = load_llm(config["llm"], callback_manager)

        # load instance specific tools
        tool_registry = load_registry(config.pop("tools", []))
        tools = tool_registry.command_prompt()

        # build messages and prompt
        system_message_prompt = SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=[],
                partial_variables={"tools": tools, "format": OUTPUT_FORMAT},
                template=INSTRUCTION_CLAUSE,
            )
        )
        human_template = "{user_input}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        chain = cls(**config, prompt=prompt)
        chain.set_callback_manager(callback_manager)

        return chain


class SavePlan(Chain):
    """Specialized chain for saving Plan and it's related Artifact"""

    def __init__(
        self,
        **data,
    ):
        super().__init__(**data)

    @property
    def _chain_type(self) -> str:
        return "ix_plan_save"

    @property
    def output_keys(self) -> List[str]:
        return ["plan_id"]

    @property
    def input_keys(self) -> List[str]:
        """Input keys this chain expects."""
        return ["ai_json"]

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save the PLAN as an artifact in the database
        """
        response = inputs["ai_json"]

        plan = Plan.objects.create(
            name=response["name"],
            description=response["description"],
            creator=self.callback_manager.task,
        )

        for command in response["commands"]:
            PlanSteps.objects.create(plan=plan, details=command)

        artifact = Artifact.objects.create(
            task=self.callback_manager.task,
            key="plan",
            name=response["name"],
            description=response["description"],
            artifact_type="PLAN",
            reference={"plan_id": str(plan.id)},
            # content={"steps": response["commands"]}
        )

        TaskLogMessage.objects.create(
            role="assistant",
            task=self.callback_manager.task,
            agent=self.callback_manager.task.agent,
            content={
                "type": "ARTIFACT",
                "artifact_type": "PLAN",
                "artifact_id": str(artifact.id),
                "reference": {"plan_id": str(plan.id)},
                # remove details after UI is updated to load artifact
                "description": response["description"],
                "steps": response["commands"],
            },
        )
        return {"plan_id": str(artifact.id)}

    async def _acall(self, inputs: Dict[str, str]) -> Dict[str, str]:
        pass

    @classmethod
    def from_config(cls, config: Dict[str, Any], callback_manager: Dict[str, Any]):
        """Load an instance from a config dictionary and runtime"""
        return cls(callback_manager=callback_manager, **config)


class RunPlan(Chain):
    tool_registry: CommandRegistry = None

    def __init__(
        self,
        tool_registry,
        **data,
    ):
        super().__init__(**data)
        self.tool_registry = tool_registry

    @property
    def _chain_type(self) -> str:
        return "ix_plan_run"

    @property
    def output_keys(self) -> List[str]:
        return ["results"]

    @property
    def input_keys(self) -> List[str]:
        """Input keys this chain expects."""
        return ["plan_id"]

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save the PLAN as an artifact in the database
        """
        plan_id = inputs["plan_id"]
        plan = Plan.objects.get(pk=plan_id)

        results = {}
        for step in plan.steps.all():
            tool_config = step.details
            tool_name = tool_config["command"]["name"]
            tool_kwargs = tool_config["command"]["args"]
            logger.info(
                f"executing task_id={self.callback_manager.task.id} tool={tool_name} kwargs={tool_kwargs}"
            )
            result = self.tool_registry.call(command_name=tool_name, **tool_kwargs)
            results[tool_name] = result

            step.is_complete = True
            step.save(update_fields=["is_complete"])

        return {"results": {}}

    async def _acall(self, inputs: Dict[str, str]) -> Dict[str, str]:
        pass

    @classmethod
    def from_config(cls, config: Dict[str, Any], callback_manager: Dict[str, Any]):
        """Load an instance from a config dictionary and runtime"""
        tool_registry = load_registry(config.pop("tools", []))

        return cls(
            callback_manager=callback_manager, tool_registry=tool_registry, **config
        )
