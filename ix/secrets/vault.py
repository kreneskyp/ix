from functools import cached_property

import hvac
from django.conf import settings
from hvac import Client
from hvac.exceptions import InvalidPath

from ix.ix_users.models import User


def get_root_client():
    """Client with root access"""
    return get_client(settings.VAULT_ROOT_KEY)


def get_token_store_client():
    """Client with access to user tokens"""
    return get_client(settings.VAULT_TOKEN__USER_TOKENS)


def get_client(token):
    """Get vault client for a user, using their token"""
    return Client(
        url=settings.VAULT_SERVER,
        token=token,
        cert=(settings.VAULT_CLIENT_CRT, settings.VAULT_CLIENT_KEY),
        verify=settings.VAULT_TLS_VERIFY,
    )


def create_user_policy(user_id):
    vault_client = get_token_store_client()
    policy = f"""
    # Allow user to read their own token
    path "secret/data/{settings.VAULT_BASE_PATH}/users/{user_id}/token" {{
        capabilities = ["read"]
    }}

    # Allow user to perform CRUD operations on arbitrary keys
    path "secret/data/{settings.VAULT_BASE_PATH}/users/{user_id}/keys/*" {{
        capabilities = ["create", "read", "update", "delete"]
    }}
    path "secret/metadata/{settings.VAULT_BASE_PATH}/users/{user_id}/keys/*" {{
        capabilities = ["read", "delete"]
    }}
    path "secret/destroy/{settings.VAULT_BASE_PATH}/users/{user_id}/keys/*" {{
        capabilities = ["update"]
    }}
    """
    vault_client.sys.create_or_update_policy(
        name=f"user_{user_id}_policy", policy=policy
    )


def create_user_token(user_id, ttl="1h"):
    vault_client = get_token_store_client()

    # HAX: for now create policy when creating the token. This might
    #      be better in user creation to limit how often it runs.
    create_user_policy(user_id)

    # Generate a new token with TTL
    policies = [f"user_{user_id}_policy"]
    new_token = vault_client.auth.token.create(
        policies=policies, ttl=ttl, renewable=True
    )

    user_token = new_token["auth"]["client_token"]
    set_user_token(user_id, user_token)
    return user_token


def get_user_token(user_id):
    vault_client = get_token_store_client()
    path = f"{settings.VAULT_BASE_PATH}/users/{user_id}/token"
    try:
        existing_token_data = vault_client.secrets.kv.v2.read_secret_version(path)
        return existing_token_data["data"]["data"]["token"]
    except InvalidPath:
        # Create and return a new token if one is not found
        return create_user_token(user_id)

    # If token is not found or another issue arises
    return None


def set_user_token(user_id, token):
    """Set a user's access token in vault"""
    vault_client = get_token_store_client()
    return vault_client.secrets.kv.v2.create_or_update_secret(
        f"{settings.VAULT_BASE_PATH}/users/{user_id}/token", secret={"token": token}
    )


def handle_new_user(user_id):
    create_user_policy(user_id)
    return create_user_token(user_id)


def delete_secrets_recursive(path=""):
    """Recursive function to delete secrets using hvac client"""
    client = get_root_client()

    try:
        list_response = client.secrets.kv.v2.list_secrets(path=path)
    except hvac.exceptions.InvalidPath:
        # either path was invalid or list was empty. Just trying to catch the
        # empty lists here but it throws InvalidPath so this might result in
        # false negatives
        list_response = None

    if list_response:
        if "keys" in list_response["data"]:
            for key in list_response["data"]["keys"]:
                new_path = f"{path}/{key}"  # Fix the path by adding a slash
                if key.endswith("/"):
                    # It's a directory, so we recurse
                    delete_secrets_recursive(new_path)
                else:
                    # It's an actual secret, so we delete
                    client.secrets.kv.v2.delete_metadata_and_all_versions(path=new_path)

    # Now that the subdirectories are empty, we can delete the current directory
    # root is not deleted.
    if path:
        client.secrets.kv.v2.delete_metadata_and_all_versions(path=path)


class UserVaultClient:
    def __init__(self, user: User, token: str = None):
        self.user = user
        self._provided_token = token

    @property
    def base_path(self):
        return f"{settings.VAULT_BASE_PATH}/users/{self.user.id}/keys"

    @cached_property
    def token(self):
        # Use the provided token if it's available.
        if self._provided_token:
            return self._provided_token

        # Otherwise, fetch the token using get_user_token.
        fetched_token = get_user_token(self.user.id)
        assert fetched_token is not None
        return fetched_token

    @cached_property
    def client(self):
        return get_client(self.token)

    def write(self, path, data):
        return self.client.secrets.kv.v2.create_or_update_secret(
            path=f"{self.base_path}/{path}", secret=data
        )

    def read(self, path):
        response = self.client.secrets.kv.v2.read_secret_version(
            path=f"{self.base_path}/{path}"
        )
        return response["data"]["data"]

    def delete(self, path):
        # Fetch the metadata of the secret which contains all the versions
        path = f"{self.base_path}/{path}"
        metadata = self.client.secrets.kv.v2.read_secret_metadata(path)

        # Extract version IDs
        version_ids = list(metadata["data"]["versions"].keys())
        print("version_id: ", version_ids)

        self.client.secrets.kv.v2.destroy_secret_versions(
            path=path, versions=version_ids
        )
