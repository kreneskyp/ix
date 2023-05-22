import logging
from typing import Dict, Any, List

from langchain.chains.base import Chain
from ix.chat.models import Artifact
from ix.commands import CommandRegistry
from ix.task_log.models import TaskLogMessage, Plan, PlanSteps


logger = logging.getLogger(__name__)


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
        return ["plan_json"]

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save the PLAN as an artifact in the database
        """
        response = inputs["plan_json"]

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
            storage={"type": "django:ix.task_log.models.Plan", "id": str(plan.id)},
        )

        TaskLogMessage.objects.create(
            role="assistant",
            task=self.callback_manager.task,
            agent=self.callback_manager.task.agent,
            parent=self.callback_manager.think_msg,
            content={
                "type": "ARTIFACT",
                "artifact_type": "PLAN",
                "artifact_id": str(artifact.id),
                "storage": {"plan_id": str(plan.id)},
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
        plan.is_draft = False
        plan.save(update_fields=["is_draft"])

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

            # save all artifacts produced by this tool
            artifacts = []
            for artifact_definition in tool_config.get("produces_artifacts", []):
                artifact = Artifact.objects.create(
                    task=self.callback_manager.task,
                    key=artifact_definition["key"],
                    name=artifact_definition["name"],
                    description=artifact_definition["description"],
                    artifact_type=artifact_definition["type"],
                    storage={
                        "type": artifact_definition["storage"],
                        "id": artifact_definition["identifier"],
                    },
                )
                artifacts.append(artifact)

            TaskLogMessage.objects.create(
                task_id=self.callback_manager.task.id,
                parent=self.callback_manager.think_msg,
                role="assistant",
                content={
                    "type": "EXECUTED",
                    "output": f"{tool_name} executed, results={results}",
                    "artifacts": [str(artifact.id) for artifact in artifacts],
                },
            )

            step.is_complete = True
            step.save(update_fields=["is_complete"])

        plan.is_complete = True
        plan.save(update_fields=["is_complete"])

        return {"results": results}

    async def _acall(self, inputs: Dict[str, str]) -> Dict[str, str]:
        pass

    @classmethod
    def from_config(cls, config: Dict[str, Any], callback_manager: Dict[str, Any]):
        """Load an instance from a config dictionary and runtime"""
        tool_registry = CommandRegistry.for_tools(config.pop("tools", []))

        return cls(
            callback_manager=callback_manager, tool_registry=tool_registry, **config
        )
