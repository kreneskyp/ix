import logging
from typing import Any, Dict

from ix.agents.process import AgentProcess, MissingCommand, UnknownCommand
from ix.agents.prompts import COMMAND_FORMAT
from ix.task_log.models import TaskLogMessage

logger = logging.getLogger(__name__)


class AutoAgent(AgentProcess):
    """
    An agent that is given goals and attempts to find a plan to achieve them.
    The agent may be pre-seeded with a plan but will build one if not given one.

    This agent is useful for general tasks and for those where a plan can't be
    known up front.
    """

    ALLOWS_AUTONOMOUS = True
    INITIAL_INPUT = (
        "Determine which next command to use, and respond in the expected format"
    )
    NEXT_COMMAND = INITIAL_INPUT

    # NEXT_COMMAND = "GENERATE NEXT COMMAND JSON"
    OUTPUT_FORMAT = COMMAND_FORMAT

    def build_base_prompt(self):
        goals_clause = "\n".join(
            [
                f"{i + 1}. {goal['description']}"
                for i, goal in enumerate(self.task.goals)
            ]
        )
        commands_clause = self.command_registry.command_prompt()
        agent = self.agent
        from ix.agents.prompts import CONSTRAINTS_CLAUSE
        from ix.agents.prompts import RESOURCES_CLAUSE
        from ix.agents.prompts import SELF_EVALUATION_CLAUSE
        from ix.agents.prompts import FORMAT_CLAUSE

        return f"""
    You are {agent.name}, {agent.purpose}
    {goals_clause}
    {CONSTRAINTS_CLAUSE}
    {commands_clause}
    {RESOURCES_CLAUSE}
    {SELF_EVALUATION_CLAUSE}
    {FORMAT_CLAUSE}
    """

    def parse_response(
        self, think_msg: TaskLogMessage, response: str
    ) -> Dict[str, Any]:
        """
        Parse the response from the user.
        """

        data = super().parse_response(think_msg, response)

        # log command to persistent storage
        log_message = TaskLogMessage.objects.create(
            task_id=self.task_id,
            parent_id=think_msg.id,
            role="assistant",
            content=dict(type="COMMAND", **data),
        )

        # validate command and then execute or seek feedback
        if (
            "command" not in data
            or "name" not in data["command"]
            or "args" not in data["command"]
            or not data["command"]
        ):
            raise MissingCommand

        elif data["command"]["name"] not in self.command_registry.commands:
            raise UnknownCommand(f'{data["command"]["name"]} is not a valid command')
        else:
            command = self.command_registry.get(data["command"]["name"])
            logger.info(f"model returned task_id={self.task_id} command={command.name}")
            return {"command": command, "message": log_message}

    def handle_response(self, execute: bool, parsed_response: dict) -> bool:
        cmd_message = parsed_response["message"]
        if execute:
            return self.msg_execute(cmd_message)
        else:
            logger.info(f"requesting user authorization task_id={self.task_id}")
            self.request_user_auth(str(cmd_message.id))

    def msg_execute(self, cmd_message: TaskLogMessage) -> bool:
        name = cmd_message.content["command"]["name"]
        kwargs = cmd_message.content["command"].get("args", {})
        try:
            result = self.execute(name, **kwargs)
            TaskLogMessage.objects.create(
                task_id=self.task_id,
                role="assistant",
                parent=cmd_message.parent,
                content={
                    "type": "EXECUTED",
                    "message_id": str(cmd_message.id),
                    "output": f"{name} executed, result={result}",
                },
            )
        except Exception as e:
            self.log_exception(e, cmd_message.parent, cmd_message)
        return True

    def execute(self, name: str, **kwargs) -> Any:
        """
        execute the command
        """
        logger.info(f"executing task_id={self.task_id} command={name} kwargs={kwargs}")
        result = self.command_registry.call(name, **kwargs)
        return result
