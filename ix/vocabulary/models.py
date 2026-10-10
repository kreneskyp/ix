from django.db import models
import uuid


class Term(models.Model):
    """
    A model representing a term in the vocabulary.
    """

    SYSTEM = "SYS"
    CHAT = "CHT"
    TASK = "TSK"
    CHAIN = "CHN"
    NODE = "NOD"

    SCOPE_CHOICES = [
        (SYSTEM, "System"),
        (CHAT, "Chat"),
        (TASK, "Task"),
        (CHAIN, "Chain"),
        (NODE, "Node"),
    ]

    related_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    term = models.CharField(max_length=255, unique=True)
    scope = models.CharField(
        max_length=3,
        choices=SCOPE_CHOICES,
        default=SYSTEM,
    )
    tags = models.CharField(max_length=255, blank=True)
    definition = models.TextField()

    def __str__(self):
        return self.term
