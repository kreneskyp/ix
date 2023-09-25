import uuid
from django.db import models

from ix.chains.models import Chain


class Agent(models.Model):
    MODEL_CHOICES = (
        ("gpt4", "GPT4"),
        ("gpt-3.5-turbo", "GPT3.5"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=63)
    purpose = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # default model config
    model = models.CharField(max_length=255)
    config = models.JSONField(default=dict)

    # agent config
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE, null=True)
    is_test = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Resource(models.Model):
    RESOURCE_TYPE_CHOICES = (
        ("vector_memory", "Vector Memory"),
        ("database", "Database"),
        ("file_system", "File System"),
        ("cache", "Cache"),
        ("api", "API"),
        ("knowledge_base", "Knowledge Base"),
        ("image_database", "Image Database"),
        ("audio_database", "Audio Database"),
        ("video_database", "Video Database"),
        ("cloud_storage", "Cloud Storage"),
        ("content_delivery_network", "Content Delivery Network"),
        ("message_queue", "Message Queue"),
        ("stream_processing", "Stream Processing"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=32, choices=RESOURCE_TYPE_CHOICES)
    config = models.JSONField()

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="resources")

    def __str__(self):
        return f"{self.type} for {self.agent.name}"
