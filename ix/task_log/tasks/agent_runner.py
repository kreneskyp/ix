from typing import Optional

from celery_singleton import Singleton
from ix.agents.process import AgentProcess
from ix.server.celery import app
from ix.task_log.models import Task

import logging

logger = logging.getLogger(__name__)


@app.task(
    base=Singleton,
    unique_on=[
        "task_id",
    ],
)
def start_agent_loop(task_id: str, message_id: Optional[str] = None):
    """
    Start agent process loop.

    This method uses celery `Singleton`. If executed again with the same `task_id`, it will not start a new process.
    An AsyncResult for the running task will be returned.

    This method expects `task_id` to be a string to be compatible with celery Singleton.
    """
    task = Task.objects.get(pk=task_id)
    logger.info(
        f"Starting agent process for task_id={task_id} agent_class_path={task.agent.agent_class_path}"
    )
    process = AgentProcess.from_task(task)
    return process.start()


@app.task(
    base=Singleton,
    unique_on=[
        "task_id",
    ],
)
def start_chat_loop(chat_id: str):
    """
    Start a Chat's agent process loop.

    The Chat's agent process loop runs an agent for the chats primary process. This can be a specific agent or
    A routing agent who directs the chat to the correct agent.

    This method uses celery `Singleton`. If executed again with the same `chat_id`, it will not start a new process.
    An AsyncResult for the running chat task will be returned.

    This method expects `chat_id` to be a string to be compatible with celery Singleton.
    """
    chat = Chat.objects.get(chat_id=chat_id)
    process = AgentProcess.from_task(chat.task)
    return process.start()
