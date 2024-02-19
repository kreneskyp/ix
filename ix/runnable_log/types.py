from datetime import datetime
from typing import Optional, List
from uuid import UUID

from langchain.schema.runnable.utils import Input, Output
from pydantic import BaseModel


class RunnableExecution(BaseModel):
    id: UUID
    node_id: UUID
    parent_id: Optional[UUID] = None
    started_at: datetime
    finished_at: datetime
    completed: bool = False
    inputs: Input = {}
    outputs: Output = {}
    message: Optional[str] = None

    class Config:
        from_attributes = True


class ExecutionGroup(BaseModel):
    task_id: UUID
    executions: List[RunnableExecution]
