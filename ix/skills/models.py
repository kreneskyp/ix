import uuid

from django.db import models

from ix.ix_users.models import OwnedModel


class Skill(OwnedModel):
    """
    A skill defined as a python script.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    description = models.TextField()
    code = models.TextField()
    func_name = models.CharField(max_length=64)
    input_schema = models.JSONField()
    tags = models.JSONField(default=list)
