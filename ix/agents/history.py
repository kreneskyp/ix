import logging
from functools import cached_property
from typing import Dict, Any, Optional, Union
from uuid import UUID

from ix.task_log.models import Task, TaskLogMessage

logger = logging.getLogger(__name__)


class TaskHistory:
    """
    Placeholder for code that updates the task history. Originally part of AgentProcess, this
    was moved here after AgentProcess was turned into a wrapper around Langchain. This code
    will likely be integrated into langchain memory classes at a later date.
    """

    # indicates if the agent should be allowed to run autonomously
    ALLOWS_AUTONOMOUS = True

    # Messages useful for humans and debugging, but aren't included in the prompt context
    EXCLUDED_MSG_TYPES = {
        "AUTH_REQUEST",
        "AUTHORIZE",
        "AUTONOMOUS",
        "FEEDBACK_REQUEST",
        "THOUGHT",
        "SYSTEM",
    }

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        self.history = []
        self.last_message = None

        self.autonomous = False

        # task init
        self.update_message_history()
        logger.info("AgentProcess initialized")

    @cached_property
    def task(self):
        return Task.objects.get(pk=self.task_id)

    def query_message_history(self, since=None):
        """Fetch message history from persistent store for context relevant messages"""

        # base query, selects messages relevant for chat context
        query = TaskLogMessage.objects.filter(task_id=self.task_id).order_by(
            "created_at"
        )

        # filter to only new messages
        if since:
            query = query.filter(created_at__gt=since)

        return query

    def update_message_history(self):
        """
        Update message history with the most recent messages since the last update.
        Initial startup will load all history into memory. Subsequent updates will
        only load new messages.
        """

        last_message_at = self.last_message.created_at if self.last_message else None
        logger.debug(
            f"AgentProcess updating message history, last_message_at={last_message_at}"
        )

        # fetch unseen messages and save the last timestamp for the next iteration
        messages = list(self.query_message_history(last_message_at))
        if messages:
            self.last_message = messages[-1]
        logger.debug(
            f"AgentProcess fetched n={len(messages)} messages from persistence"
        )

        # process AUTONOMOUS messages if supported by the agent
        # toggle autonomous mode based on latest AUTONOMOUS message
        if self.ALLOWS_AUTONOMOUS:
            for message in reversed(messages):
                if message.content["type"] == "AUTONOMOUS":
                    autonomous = message.content["enabled"]
                    if autonomous != self.autonomous:
                        self.autonomous = autonomous
                        logger.info(
                            f"AgentProcess toggled autonomous mode to {autonomous}"
                        )
                    break

        # format all message instance for use in the prompt
        formatted_messages = [
            message.as_message()
            for message in messages
            if message.content["type"] not in self.EXCLUDED_MSG_TYPES
        ]
        self.add_history(*formatted_messages)

        logger.info(
            f"AgentProcess loaded n={len(messages)} chat messages from persistence"
        )

    def get_input(self, input_id: Optional[UUID] = None) -> Union[Dict[str, Any], bool]:
        """get input for chain"""

        # 1. use input_id message if present
        if input_id:
            message = TaskLogMessage.objects.get(id=input_id)
            return {"user_input": message.content["feedback"]}

        # 2. load the last message from the queue
        try:
            self.last_message = TaskLogMessage.objects.filter(
                task_id=self.task_id
            ).latest("created_at")
        except TaskLogMessage.DoesNotExist:
            self.last_message = None

        logger.debug(f"task_id={self.task_id} last message={self.last_message}")

        if not self.last_message:
            logger.info(f"first tick for task_id={self.task_id}")
            return {"user_input": self.INITIAL_INPUT}
            # TODO load initial auth from either message stream or task

        elif self.last_message.content["type"] == "FEEDBACK":
            return {"user_input": self.last_message.content["feedback"]}

        elif self.last_message.content["type"] == "AUTHORIZE":
            logger.info(f"resuming with user authorization for task_id={self.task_id}")
            # auth/feedback resume, run command that was authorized
            # by default only a single command is authorized.
            # authorized_for = self.last_message.content.get("n", 1) - 1
            authorized_msg = TaskLogMessage.objects.get(
                pk=self.last_message.content["message_id"]
            )
            [reference_field, reference_value] = list(
                authorized_msg.content["storage"].items()
            )[0]
            return dict(
                user_input=f"execute {reference_field}={reference_value}",
                **authorized_msg.content["storage"],
            )

        elif self.last_message.content["type"] in ["AUTH_REQUEST", "FEEDBACK_REQUEST"]:
            # if last message is an unfulfilled feedback request then exit
            logger.info(
                f"Exiting, missing response to type={self.last_message.content['type']}"
            )
            return False

    def add_history(self, *history_messages: Dict[str, Any]):
        logger.debug(f"adding history history_messages={history_messages}")
        self.history.extend(history_messages)
