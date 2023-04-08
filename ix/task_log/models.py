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
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    goals = models.JSONField(null=True, blank=True)
    goals_complete = models.JSONField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    complete_at = models.DateTimeField(null=True, blank=True)


class TaskLogMessage(models.Model):
    """
    TaskLog model represents a log entry containing agent, user, goals, user response,
    command, and timestamps for the assistant and user interactions.
    """

    task = models.ForeignKey(Task, default=None, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, default=None, on_delete=models.CASCADE)
    authorized = models.BooleanField(null=True, blank=True)
    user_response = models.TextField(null=True, blank=True)
    command = models.JSONField(null=True, blank=True)
    assistant_timestamp = models.DateTimeField(auto_now_add=True)
    user_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-assistant_timestamp"]

    def __str__(self) -> str:
        return f"TaskLogMessage {self.id} ({self.agent})"
