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

    def get_agent_process(self):
        from ix.agents.process import AgentProcess

        return AgentProcess.from_task(self)


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
    task = models.ForeignKey(
        Task, default=None, on_delete=models.CASCADE, related_name="messages"
    )
    agent = models.ForeignKey(Agent, null=True, default=None, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        "self", null=True, default=None, on_delete=models.CASCADE
    )

    # message content
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.JSONField()

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"TaskLogMessage {self.id} ({self.role}, {self.content['type']})"

    def as_message(self):
        content = self.content.copy()
        content_type = content.pop("type")
        # Map SYSTEM messages to USER role
        #
        # SYSTEM messages that are included as history must be converted to the USER role. SYSTEM is a special meaning
        # that configures the agent. Messages must either be ASSISTANT or USER for the model to interpret it as
        # conversation.
        if self.role == "system":
            role = "user"
        else:
            role = self.role

        # return content_type specific formatting to tune AI response
        if content_type == "FEEDBACK":
            content_str = content["feedback"]
        elif content_type == "THINK":
            content_str = content["input"]
        else:
            # default to dumping json datum
            content_str = json.dumps(content, sort_keys=True)

        return {
            "role": role.lower(),
            "content": content_str,
        }


class Artifact(models.Model):
    """
    Artifacts represent an object or data created by an Agent. Artifacts are bits of information
    that are either a user deliverable or an input to a further step.

    This model stores precise information about the artifact. The artifact itself may be stored
    elsewhere such as a filesystem or database.

    References to artifacts may also be stored in vector databases for similarity search.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="artifacts")
    key = models.CharField(max_length=128)
    artifact_type = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reference = models.JSONField()


class Plan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="created_plans"
    )
    runner = models.ForeignKey(
        Task, on_delete=models.CASCADE, null=True, related_name="ran_plans"
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_draft = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class PlanSteps(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="steps")
    is_complete = models.BooleanField(default=False)
    # agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="steps")
    details = models.JSONField()

    def __str__(self):
        return f"{self.plan.name} step {self.order}"
