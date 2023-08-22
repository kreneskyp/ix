import logging
import re
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
from uuid import UUID

from django.db.models import Q

from ix.api.chains.endpoints import DeletedItem
from ix.chains.management.commands.create_coder_v2 import CODER_V2_AGENT
from ix.chains.management.commands.create_ix_v2 import IX_AGENT_V2
from ix.chat.models import Chat, Task
from ix.agents.models import Agent
from ix.api.agents.types import Agent as AgentPydantic
from ix.api.chats.types import (
    ChatGraph,
    ChatNew,
    ChatUpdate,
    Chat as ChatPydantic,
    Task as TaskPydantic,
    Plan as PlanPydantic,
    Artifact as ArtifactPydantic,
    ChatAgentAction,
    ChatMessage,
    ChatInput,
    ChatInList,
    ChatQueryPage,
    ChatMessageQueryPage,
)
from ix.task_log.models import UserFeedback, TaskLogMessage
from ix.task_log.tasks.agent_runner import (
    start_agent_loop,
)


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chats/", response_model=ChatPydantic, tags=["Chats"])
async def create_chat(chat: ChatNew):
    user = await User.objects.alatest("id")

    # TODO: turn this on once auth is setup for UI
    # user = info.context.user
    if user.is_anonymous:
        raise Exception(
            "Authentication is required to create a task."
        )  # pragma: no cover

    # If agent is not provided, use the default agent
    if chat.lead_id:
        lead = await Agent.objects.aget(pk=chat.lead_id)
    else:
        lead = await Agent.objects.aget(pk=IX_AGENT_V2)

    task = await Task.objects.acreate(
        name=chat.name,
        user=user,
        agent=lead,
        chain_id=lead.chain_id,
        autonomous=chat.autonomous,
    )

    chat_obj = await Chat.objects.acreate(
        task=task,
        lead=lead,
        name=chat.name,
    )

    code = await Agent.objects.aget(id=CODER_V2_AGENT)
    await chat_obj.agents.aadd(code)

    return ChatPydantic.model_validate(chat_obj)


@router.get("/chats/{chat_id}", response_model=ChatPydantic, tags=["Chats"])
async def get_chat(chat_id: UUID):
    try:
        chat = await Chat.objects.aget(pk=chat_id)
    except Chat.DoesNotExist:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatPydantic.model_validate(chat)


@router.get("/chats/", response_model=ChatQueryPage, tags=["Chats"])
async def get_chats(search: Optional[str] = None, limit: int = 10, offset: int = 0):
    query = (
        Chat.objects.filter(Q(name__icontains=search)) if search else Chat.objects.all()
    )
    query = query.order_by("-created_at")

    # punting on async implementation of pagination until later
    return await sync_to_async(ChatQueryPage.paginate)(
        output_model=ChatInList, queryset=query, limit=limit, offset=offset
    )


@router.put("/chats/{chat_id}", response_model=ChatPydantic, tags=["Chats"])
async def update_chat(chat_id: UUID, chat: ChatUpdate):
    try:
        chat_obj = await Chat.objects.aget(pk=chat_id)
    except Chat.DoesNotExist:
        raise HTTPException(status_code=404, detail="Chat not found")

    for attr, value in chat.model_dump().items():
        if value is not None:
            setattr(chat_obj, attr, value)
    await chat_obj.asave()

    return ChatPydantic.model_validate(chat_obj)


@router.delete("/chats/{chat_id}", response_model=DeletedItem, tags=["Chats"])
async def delete_chat(chat_id: UUID):
    try:
        chat = await Chat.objects.aget(pk=chat_id)
        await chat.adelete()
        return DeletedItem(id=chat_id)
    except Chat.DoesNotExist:
        raise HTTPException(status_code=404, detail="Chat not found")


@router.delete(
    "/chats/{chat_id}/agents/{agent_id}", response_model=ChatAgentAction, tags=["Chats"]
)
async def remove_agent(chat_id: UUID, agent_id: UUID):
    try:
        chat = await Chat.objects.aget(pk=chat_id)
        agent = await Agent.objects.aget(pk=agent_id)
        await chat.agents.aremove(agent)
        return ChatAgentAction(chat_id=chat.id, agent_id=agent.id)
    except Chat.DoesNotExist:
        raise HTTPException(status_code=404, detail="Chat does not exist.")
    except Agent.DoesNotExist:
        raise HTTPException(status_code=404, detail="Agent does not exist.")


@router.put(
    "/chats/{chat_id}/agents/{agent_id}", response_model=ChatAgentAction, tags=["Chats"]
)
async def add_agent(chat_id: UUID, agent_id: UUID):
    try:
        chat = await Chat.objects.aget(pk=chat_id)
        agent = await Agent.objects.aget(pk=agent_id)

        # Check if the agent is already a lead or an agent
        if chat.lead_id == agent.id or await chat.agents.filter(id=agent.id).aexists():
            return ChatAgentAction(chat_id=chat.id)

        await chat.agents.aadd(agent)
        await chat.asave()
        return ChatAgentAction(chat_id=chat.id, agent_id=agent.id)
    except Chat.DoesNotExist:
        raise HTTPException(status_code=404, detail="Chat does not exist.")
    except Agent.DoesNotExist:
        raise HTTPException(status_code=404, detail="Agent does not exist.")


@router.get("/chats/{chat_id}/graph", response_model=ChatGraph, tags=["Chats"])
async def get_chat_graph(chat_id: str):
    """Chat and related objects

    Single object containing objects needed to render the chat view.

    TODO: this should be broken apart into smaller queries so the UI can
          load this incrementally.
    """
    chat = await Chat.objects.aget(pk=chat_id)
    lead = await Agent.objects.aget(pk=chat.lead_id)
    task = await Task.objects.aget(pk=chat.task_id)
    agents = [AgentPydantic.model_validate(agent) async for agent in chat.agents.all()]
    plans = [
        PlanPydantic.model_validate(plan) async for plan in task.created_plans.all()
    ]
    artifacts = [
        ArtifactPydantic.model_validate(artifact)
        async for artifact in task.artifacts.all()
    ]
    return ChatGraph(
        chat=ChatPydantic.model_validate(chat),
        lead=AgentPydantic.model_validate(lead),
        agents=agents,
        plans=plans,
        task=TaskPydantic.model_validate(task),
        artifacts=artifacts,
    )


def get_artifacts(user_input):
    """Find all references to artifacts in user input."""
    # Pattern to find all instances of text enclosed in curly braces.
    pattern = r"\{(.*?)\}"

    # re.findall returns all non-overlapping matches of pattern in string, as a list of strings.
    # The string is scanned left-to-right, and matches are returned in the order found.
    matches = re.findall(pattern, user_input)

    # Return the list of matches.
    return matches


@router.get(
    "/chats/{chat_id}/messages", response_model=ChatMessageQueryPage, tags=["Chats"]
)
async def get_messages(chat_id, limit: int = 10, offset: int = 0):
    chat = await Chat.objects.aget(pk=chat_id)
    task_id = chat.task_id
    query = TaskLogMessage.objects.filter(
        Q(task_id=task_id) | Q(task__parent_id=task_id)
    ).order_by("created_at")

    # punting on async implementation of pagination until later
    return await sync_to_async(ChatMessageQueryPage.paginate)(
        output_model=ChatMessage, queryset=query, limit=limit, offset=offset
    )


@router.post("/chats/{chat_id}/messages", response_model=ChatMessage, tags=["Chats"])
async def send_message(chat_id: str, chat_input: ChatInput):
    chat = await Chat.objects.aget(pk=chat_id)
    text = chat_input.text

    # save to persistent storage
    message = await TaskLogMessage.objects.acreate(
        task_id=chat.task_id,
        role="USER",
        content=UserFeedback(
            type="FEEDBACK",
            feedback=text,
        ),
    )

    # determine if user targeted a specific agent in the chat
    # if so, forward the message to that agent
    # otherwise, forward the message to the lead agent
    task_id = chat.task_id
    user_input = text.strip().lower()
    if user_input.startswith("@"):
        # Find the first space or the end of the string
        space_index = user_input.find(" ")
        if space_index == -1:
            space_index = len(user_input)  # pragma: no cover

        # Extract the agent name and find the agent
        agent_alias = user_input[1:space_index]

        agent = await Agent.objects.filter(
            Q(leading_chats=chat, alias=agent_alias)
            | Q(chats__id=chat.id, alias=agent_alias)
        ).aget()

        # delegate the task to the agent and run in this thread
        task = await Task.objects.aget(pk=chat.task_id)
        subtask = await task.adelegate_to_agent(agent)
        task_id = subtask.id
    else:
        agent = await Agent.objects.aget(pk=chat.lead_id)

    # resume task loop
    logger.info(
        f"Requesting agent loop resume chat_id={chat.id} task_id={message.task_id} user_input={message.pk}"
    )

    inputs = {
        "user_input": text,
        "chat_id": str(chat.id),
        "artifact_keys": get_artifacts(user_input) or [],
    }

    # Start agent loop. This does NOT check if the loop is already running
    # the agent_runner task is responsible for blocking duplicate runners
    await start_agent(task_id, agent, inputs)

    return ChatMessage.model_validate(message)


async def start_agent(task_id: UUID, agent: Agent, inputs: Dict[str, Any]):
    """Shim for start_agent_loop

    The async decorator on start_agent_loop sometimes causes issues in tests.
    Moving the function into this shim allows it to work correctly.
    """
    return start_agent_loop.delay(str(task_id), str(agent.chain_id), inputs=inputs)
