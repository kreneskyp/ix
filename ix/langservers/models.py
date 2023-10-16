from uuid import uuid4
from django.db import models
from ix.ix_users.models import OwnedModel


class LangServer(OwnedModel):
    """
    A record for a LangServer server. This may be an external server
    or an internal server.

    This model caches the routes and their specs. This enables chains and other
    components to be able to invoke the LangServer without needing to fetch the
    specs from the LangServer.
    """

    id = models.UUIDField(primary_key=True, default=uuid4)

    name = models.CharField(max_length=100)
    description = models.TextField()
    url = models.URLField()

    # routes provided by the LangServer in shape of Dict[str, RemoteRunnableConfig]
    routes = models.JSONField()

    # Headers to send with requests in shape of Dict[str, str]
    headers = models.JSONField()

    def __str__(self):
        return self.name
