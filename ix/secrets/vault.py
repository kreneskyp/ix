from functools import cached_property

from django.conf import settings
from hvac import Client
from hvac.exceptions import InvalidPath

from ix.ix_users.models import User


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
    path "secrets/data/users/{user_id}/token" {{
        capabilities = ["read"]
    }}

    # Allow user to perform CRUD operations on arbitrary keys
    path "secrets/data/users/{user_id}/keys/*" {{
        capabilities = ["create", "read", "update", "delete"]
    }}
    """
    vault_client.sys.create_or_update_policy(
        name=f"user_{user_id}_policy", policy=policy
    )


def create_user_token(user_id, ttl="1h"):
    vault_client = get_token_store_client()

    # Generate a new token with TTL
    # TODO: using root policy for now. User policy wasn't granting permissions
    #       unblocking by using root for now.
    # policies = [f"user_{user_id}_policy"]
    policies = ["root"]
    new_token = vault_client.auth.token.create(
        policies=policies, ttl=ttl, renewable=True
    )

    user_token = new_token["auth"]["client_token"]
    set_user_token(user_id, user_token)
    return user_token


def get_user_token(user_id):
    vault_client = get_token_store_client()
    path = f"secrets/data/users/{user_id}/token"
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
        f"secrets/data/users/{user_id}/token", secret={"token": token}
    )


def handle_new_user(user_id):
    create_user_policy(user_id)
    return create_user_token(user_id)


class UserVaultClient:
    def __init__(self, user: User, token: str = None):
        self.user = user
        self._provided_token = token

    @property
    def base_path(self):
        return f"users/{self.user.id}/keys"

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
