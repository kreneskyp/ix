import uuid

from django.db import models

from ix.chains.models import ChainNode
from ix.ix_users.models import OwnedModel
from ix.task_log.models import Task


class RunnableExecution(OwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
    parent_id = models.UUIDField(null=True)
    node = models.ForeignKey(ChainNode, on_delete=models.CASCADE, null=True)
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True)
    completed = models.BooleanField(default=False)
    inputs = models.JSONField(default=dict, null=True)
    outputs = models.JSONField(default=dict, null=True)
    message = models.TextField(null=True)

    class Meta:
        ordering = ["task", "started_at"]
