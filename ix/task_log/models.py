import json
import uuid
from typing import TypedDict, Optional

from django.contrib.auth import get_user_model
from django.db import models
from ix.agents.models import Agent
from ix.chains.models import Chain
from ix.commands.filesystem import read_file
from ix.ix_users.models import OwnedModel


class Task(models.Model):
    """An instance of an agent running."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    root = models.ForeignKey(
        "self",
        related_name="descendants",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    parent = models.ForeignKey(
        "self", related_name="children", null=True, blank=True, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=64)
    user = models.ForeignKey("ix_users.User", on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, null=True, on_delete=models.CASCADE)
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    complete_at = models.DateTimeField(null=True, blank=True)
    autonomous = models.BooleanField(default=True)

    def get_agent_process(self):
        from ix.agents.process import AgentProcess

        return AgentProcess.from_task(self)

    def delegate_to_agent(self, agent: Agent) -> "Task":
        """
        Create a subtask in which a delegated task will run.
        """
        return Task.objects.create(
            root_id=self.root_id or self.id,
            parent=self,
            name=f"delegating to agent {agent.alias}",
            agent_id=agent.id,
            chain=agent.chain,
            autonomous=self.autonomous,
            user=self.user,
        )

    async def adelegate_to_agent(self, agent: Agent) -> "Task":
        """
        Create a subtask in which a delegated task will run.
        """
        user_model = get_user_model()
        chain = await Chain.objects.aget(id=agent.chain_id)
        user = await user_model.objects.aget(id=self.user_id)
        return await Task.objects.acreate(
            root_id=self.root_id or self.id,
            parent=self,
            name=f"delegating to agent {agent.alias}",
            agent_id=agent.id,
            chain=chain,
            autonomous=self.autonomous,
            user=user,
        )


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
        ("SYSTEM", "SYSTEM"),
        ("ASSISTANT", "ASSISTANT"),
        ("USER", "USER"),
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


class Artifact(OwnedModel):
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
    storage = models.JSONField()

    @property
    def data(self):
        """Fetch related data for this artifact"""
        storage_type = self.storage["type"]
        storage_id = self.storage["id"]
        if storage_type == "write_to_file":
            # TODO: should push this out to a storage subsystem.
            return read_file(storage_id)
        return None

    def as_memory_text(self):
        """
        Return a string representation of this artifact for inclusion in prompts
        """
        return f"""
id: {self.id}
key: {self.key}
type: {self.artifact_type}
desc: {self.description}
storage_id: {self.storage["id"]}
data:
{self.data}
"""


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
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class PlanSteps(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="steps")
    is_complete = models.BooleanField(default=False)
    details = models.JSONField()
    order = models.IntegerField(null=True, default=None)

    @staticmethod
    def get_default_order(instance: "PlanSteps") -> int:
        siblings = PlanSteps.objects.filter(plan=instance.plan)
        max_order = siblings.aggregate(models.Max("order"))["order__max"]
        return (max_order or 0) + 1

    def save(self, *args, **kwargs):
        if self.order is None:
            self.order = type(self).get_default_order(self)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.details['name']}"
