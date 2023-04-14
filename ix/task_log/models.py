import json
from typing import TypedDict, Optional

from django.db import models


class Agent(models.Model):
    """
    Agent model represents an agent with a unique name and a purpose.
    """

    name = models.CharField(max_length=255, unique=True)
    purpose = models.TextField()

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=64)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    goals = models.JSONField(null=True, blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    complete_at = models.DateTimeField(null=True, blank=True)


class UserFeedback(TypedDict):
    authorized_for: int
    feedback: Optional[str]


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
        ("system", "system"),
        ("assistant", "assistant"),
        ("feedback_request", "feedback_request"),
        ("feedback", "feedback"),
        ("authorize", "authorize"),
        ("continuous", "continuous"),
        ("auth_request", "auth_request"),
        ("execute", "execute"),
    ]

    # message metadata
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
        return {
            "role": self.role.lower(),
            "content": json.dumps(content, sort_keys=True),
        }
