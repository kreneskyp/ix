import uuid

from django.db import models

from ix.ix_users.models import OwnedModel


class Schema(OwnedModel):
    """
    A schema used to define the structure of data for APIs,
    data generation, data extraction, and data transformation.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(choices=[("json", "json"), ("openapi", "openapi")])
    name = models.CharField(max_length=128)
    description = models.TextField()
    value = models.JSONField(default=dict)
    meta = models.JSONField(default=dict)


class Data(OwnedModel):
    """A data object using a defined schema.

    Persistant JSON data object that can be used by IX for many purposes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    description = models.TextField()
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE, null=True)
    value = models.JSONField(default=dict)
    meta = models.JSONField(default=dict)
