import json
import uuid
from typing import TypedDict, Optional

from django.db import models
from ix.agents.models import Agent


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    goals = models.JSONField(null=True, blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    complete_at = models.DateTimeField(null=True, blank=True)
    autonomous = models.BooleanField(default=True)


class UserFeedback(TypedDict):
    type: str
    feedback: Optional[str]
    message_id: Optional[str]


class TaskLogMessage(models.Model):
    """
    TaskLog model represents a log entry containing agent, user, goals, user response,
    command, and timestamps for the assistant and user interactions.
    """

    ROLE_CHOICES = [
        ("system", "system"),
        ("assistant", "assistant"),
        ("user", "user"),
    ]

    TYPE_CHOICES = [
        ("assistant", "assistant"),
        ("auth_request", "auth_request"),
        ("authorize", "authorize"),
        ("autonomous", "autonomous"),
        ("execute", "execute"),
        ("feedback_request", "feedback_request"),
        ("feedback", "feedback"),
        ("system", "system"),
        ("error", "error"),
    ]

    # message metadata
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, default=None, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, null=True, default=None, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # message content
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.JSONField()

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"TaskLogMessage {self.id} ({self.role}, {self.content['type']})"

    def as_message(self):
        content = self.content.copy()
        content.pop("type")
        # Map SYSTEM messages to USER role
        #
        # SYSTEM messages that are included as history must be converted to the USER role. SYSTEM is a special meaning
        # that configures the agent. Messages must either be ASSISTANT or USER for the model to interpret it as
        # conversation.
        if self.role == "system":
            role = "user"
        else:
            role = self.role

        return {
            "role": role.lower(),
            "content": json.dumps(content, sort_keys=True),
        }
