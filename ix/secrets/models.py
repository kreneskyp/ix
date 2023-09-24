import uuid
from django.db import models
from ix.ix_users.models import User


class Secret(models.Model):
    """
    Catalogs a secrets that exist for a user in vault. This model provides a
    searchable store of secrets that can be used to populate forms and other
    UI elements.

    Secret type specifies the type of secret, such as Github, AWS, etc.

    Users may store multiple copies of the same secret tracked by index. This
    enables users to configure up tp 2,147,483,647 accounts for the same service.

    Note: when resolving fetch directly from vault using the path and index
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def path(self):
        """Path to secret in database relative from users root

        Path should only show information relative to the user's root.
        Hide full path from API.
        """
        return f"{self.type}/{self.id}"
