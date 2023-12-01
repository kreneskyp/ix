import asyncio
from typing import Dict, Any

from celery_singleton import Singleton

from ix.agents.models import Agent
from ix.agents.process import AgentProcess
from ix.chains.models import Chain
from ix.chat.models import Chat
from ix.server.celery import app
from ix.task_log.models import Task

import logging

from ix.utils.asyncio import sync

logger = logging.getLogger(__name__)


@app.task(
    base=Singleton,
    unique_on=[
        "task_id",
        "chain_id",
    ],
)
@sync
async def start_agent_loop(
    task_id: str,
    user_id: str,
    chain_id: str = None,
    inputs: Dict[str, Any] = None,
):
    """
    Start agent process loop.

    This method uses celery `Singleton`. If executed again with the same `task_id`, it will not start a new process.
    An AsyncResult for the running task will be returned.

    This method expects `task_id` to be a string to be compatible with celery Singleton.
    """
    agent, chain = await asyncio.gather(
        Agent.objects.aget(task__id=task_id),
        Chain.objects.aget(pk=chain_id),
    )

    chat_subtask = await Task.objects.acreate(
        parent_id=task_id,
        agent_id=agent.id,
        chain_id=chain_id,
        user_id=user_id,
    )

    process = AgentProcess(chat_subtask, agent, chain)
    return await process.start(inputs)


@app.task(
    base=Singleton,
    unique_on=["chat_id", "chain_id"],
)
def start_chat_loop(
    task_id: str, chat_id: str, chain_id: str, inputs: Dict[str, Any] = None
):
    """
    Start a Chat's agent process loop.

    The Chat's agent process loop runs an agent for the chats primary process. This can be a specific agent or
    A routing agent who directs the chat to the correct agent.

    This method uses celery `Singleton`. If executed again with the same `chat_id`, it will not start a new process.
    An AsyncResult for the running chat task will be returned.

    This method expects `chat_id` to be a string to be compatible with celery Singleton.
    """
    chat = Chat.objects.get(pk=chat_id)
    task = chat.task
    logger.info(
        f"Starting agent process for agent={task.agent.name} task_id={task_id} user_input={inputs}"
    )
    process = AgentProcess(task_id, chain_id)
    return process.start(inputs)
