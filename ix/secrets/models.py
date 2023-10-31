import uuid
from django.db import models
from ix.ix_users.models import OwnedModel, User
from ix.secrets.vault import UserVaultClient


class SecretType(OwnedModel):
    """
    Defines type of secret and the fields it stores. Secrets may contain a
    dict (depth=1) of secrets. This model defines the type and a json schema
    of the fields it stores.

    This model gives a way to "cache" secret types generated from component
    configs when importing them.

    It also enables user defined types.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    # A JSON Schema for a depth=1 dict of fields stored by this type of secret
    fields_schema = models.JSONField()


class Secret(OwnedModel):
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
    type = models.ForeignKey(SecretType, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def path(self):
        return f"{self.type_id}/{self.id}"

    @property
    def client(self):
        # TODO: make this configurable for production
        # return UserVaultClient(user=self.user)
        return SecretValueClient()

    async def get_client(self):
        # TODO: make this configurable for production
        # user = await User.objects.aget(id=self.user_id)
        return SecretValueClient()

    def read(self):
        return self.client.read(self.path)

    def write(self, value):
        return self.client.write(self.path, value)

    def delete_secure(self):
        return self.client.delete(self.path)

    async def aread(self):
        client = await self.get_client()
        return await client.aread(self.path)

    async def awrite(self, value):
        client = await self.get_client()
        return await client.awrite(self.path, value)

    async def adelete_secure(self):
        client = await self.get_client()
        return await client.adelete(self.path)


class MissingSecret(Exception):
    pass


class SecretValueClient:
    def read(self, path: str):
        return SecretValue.objects.get(path=path).data

    async def aread(self, path: str):
        try:
            secret_value = await SecretValue.objects.aget(path=path)
        except SecretValue.DoesNotExist:
            raise MissingSecret()
        return secret_value.data

    def write(self, path: str, value: dict):
        try:
            secret_value = SecretValue.objects.get(path=path)
        except SecretValue.DoesNotExist:
            secret_value = SecretValue(path=path)
        secret_value.data = value
        secret_value.save()

    async def awrite(self, path: str, value: dict):
        try:
            secret_value = await SecretValue.objects.aget(path=path)
        except SecretValue.DoesNotExist:
            secret_value = SecretValue(path=path)
        secret_value.data = value
        await secret_value.asave()

    def delete(self, path: str):
        try:
            SecretValue.objects.get(path=path).delete()
        except SecretValue.DoesNotExist:
            pass

    async def adelete(self, path: str):
        try:
            secret_value = await SecretValue.objects.aget(path=path)
            await secret_value.adelete()
        except SecretValue.DoesNotExist:
            raise MissingSecret()


class SecretValue(models.Model):
    """SecretValue storage for dev environments

    This is an UNENCRYPTED mock secret storage system that is intended for use
    ONLY FOR DEVELOPMENT. This is intended for use in place of vault since vault
    is annoying to configure for dev environments.
    """

    path = models.CharField(max_length=(36 * 2) + 1)
    data = models.JSONField()
