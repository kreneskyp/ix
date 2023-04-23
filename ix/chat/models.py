import uuid

from django.db import models
from ix.agents.models import Agent, Resource
from ix.task_log.models import Task, Artifact


class Chat(models.Model):
    """
    A chat is a conversation between one or more agents. A chat includes a lead agent who
    is responsible for the chat. The lead agent will respond or delegate questions to other
    agents.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    lead = models.ForeignKey(
        Agent, on_delete=models.CASCADE, related_name="leading_chats"
    )
    agents = models.ManyToManyField(Agent, related_name="chats")
    tasks = models.ManyToManyField(Task, related_name="chats")
    artifacts = models.ManyToManyField(Artifact, related_name="chats")
    resources = models.ManyToManyField(Resource, related_name="chats")

    # TODO: this is a placeholder for now until TaskLogMessage can be converted to ChatMessage
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="leading_chats"
    )

    def get_agent_process(self):
        return self.agent.get_agent_process(self.task)
