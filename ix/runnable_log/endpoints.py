from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from fastapi import APIRouter, Depends
from uuid import UUID
from ix.api.auth import get_request_user

__all__ = ["router", "get_task_execution_log"]

from ix.chains.models import Chain

from ix.runnable_log.models import RunnableExecution
from ix.runnable_log.types import (
    ExecutionGroup,
    RunnableExecution as RunnableExecutionPydantic,
)
from ix.task_log.models import Task

router = APIRouter()


async def _get_execution_log(task_id: UUID, user: AbstractUser) -> ExecutionGroup:
    query = RunnableExecution.filtered_owners(user=user).filter(task_id=task_id)

    entries = []
    async for row in query:
        entries.append(RunnableExecutionPydantic.model_validate(row))

    return ExecutionGroup(task_id=task_id, executions=entries)


@router.get("/runs/{chain_id}/latest/log", response_model=ExecutionGroup, tags=["runs"])
async def get_latest_execution_log(
    chain_id: UUID, user: AbstractUser = Depends(get_request_user)
) -> ExecutionGroup:
    chain = await Chain.filtered_owners(user=user).aget(id=chain_id)
    task = await Task.objects.filter(
        Q(chain_id=chain.id) | Q(root__chain_id=chain.id)
    ).alatest("created_at")
    return await _get_execution_log(task.id, user)


@router.get(
    "/runs/{chain_id}/{task_id}/log", response_model=ExecutionGroup, tags=["runs"]
)
async def get_task_execution_log(
    task_id: UUID, user: AbstractUser = Depends(get_request_user)
) -> ExecutionGroup:
    return await _get_execution_log(task_id, user)
