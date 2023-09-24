from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from asgiref.sync import sync_to_async

from ix.api.auth import get_request_user
from ix.api.chains.endpoints import DeletedItem
from ix.api.secrets.types import (
    Secret as SecretPydantic,
    SecretPage,
    CreateSecret,
    UpdateSecret,
)
from ix.secrets.models import Secret
from ix.secrets.vault import UserVaultClient
from ix.ix_users.models import User

router = APIRouter()


@router.post("/secrets/", response_model=SecretPydantic, tags=["Secrets"])
async def create_secret(
    secret: CreateSecret, current_user: User = Depends(get_request_user)
):
    # Record secret in database
    secret_kwargs = secret.dict(
        exclude={"id", "user_id", "value", "created_at", "updated_at"}
    )
    secret_obj = Secret(user_id=current_user.id, **secret_kwargs)
    await secret_obj.asave()

    # write to vault
    client = UserVaultClient(user=current_user)
    client.write(secret_obj.path, secret.value)

    return SecretPydantic.from_orm(secret_obj)


@router.get(
    "/secrets/{secret_id}",
    response_model=SecretPydantic,
    tags=["Secrets"],
)
async def get_secret(secret_id: UUID, current_user: User = Depends(get_request_user)):
    try:
        secret = await Secret.objects.aget(pk=secret_id, user_id=current_user.id)
    except Secret.DoesNotExist:
        raise HTTPException(status_code=404, detail="Secret not found")
    return SecretPydantic.from_orm(secret)


@router.put(
    "/secrets/{secret_id}",
    response_model=SecretPydantic,
    tags=["Secrets"],
)
async def update_secret(
    secret_id: UUID,
    secret: UpdateSecret,
    current_user: User = Depends(get_request_user),
):
    try:
        secret_obj = await Secret.objects.aget(pk=secret_id, user_id=current_user.id)
    except Secret.DoesNotExist:
        raise HTTPException(status_code=404, detail="Secret not found")

    # update DB if needed
    has_db_update = False
    for attr, value in secret.dict().items():
        if hasattr(secret_obj, attr) and getattr(secret_obj, attr) != value:
            setattr(secret_obj, attr, value)
            has_db_update = True
    if has_db_update:
        await secret_obj.asave()

    # update vault value
    client = UserVaultClient(user=current_user)
    client.write(secret_obj.path, secret.value)

    return SecretPydantic.from_orm(secret_obj)


@router.get("/secrets/", response_model=SecretPage, tags=["Secrets"])
async def get_secrets(
    path: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(
        get_request_user
    ),  # Assuming this function is already defined
):
    """List endpoint used to retrieve secret metadata from the database.

    Secret values must be fetched from vault. This endpoint fetches secrets for
    use rendering choices in the UX. (e.g. to show a list of choices)
    """
    query = Secret.objects.filter(user_id=current_user.id)
    if path:
        query = query.filter(path=path)

    # Handling pagination manually for this example
    query = query[offset : offset + limit]

    # punting on async implementation of pagination until later
    return await sync_to_async(SecretPage.paginate)(
        output_model=SecretPydantic, queryset=query, limit=limit, offset=offset
    )


@router.delete("/secrets/{secret_id}", response_model=DeletedItem, tags=["Secrets"])
async def delete_secret(
    secret_id: UUID, current_user: User = Depends(get_request_user)
):
    try:
        secret = await Secret.objects.aget(pk=secret_id, user_id=current_user.id)
    except Secret.DoesNotExist:
        raise HTTPException(status_code=404, detail="Secret not found")

    await secret.adelete()
    return DeletedItem(id=str(secret_id))
