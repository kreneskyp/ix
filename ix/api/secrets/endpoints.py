from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from asgiref.sync import sync_to_async

from ix.api.auth import get_request_user
from ix.api.chains.endpoints import DeletedItem
from ix.api.secrets.types import (
    SecretType as SecretTypePydantic,
    SecretTypeEdit,
    SecretTypePage,
    Secret as SecretPydantic,
    SecretPage,
    CreateSecret,
    UpdateSecret,
)
from ix.secrets.models import SecretType, Secret
from ix.secrets.vault import UserVaultClient
from ix.ix_users.models import User

router = APIRouter()


@router.post("/secret_types/", response_model=SecretTypePydantic, tags=["Secrets"])
async def create_secret_type(
    secret_type: SecretTypeEdit,
    user: User = Depends(get_request_user),
):
    # create a new SecretType
    secret_type_obj = await SecretType.objects.acreate(
        user_id=user.id,
        **secret_type.model_dump(),
    )
    return SecretTypePydantic.from_orm(secret_type_obj)


@router.get(
    "/secret_types/{secret_type_id}",
    response_model=SecretTypePydantic,
    tags=["Secrets"],
)
async def get_secret_type(secret_type_id: UUID, user: User = Depends(get_request_user)):
    try:
        secret_type = await SecretType.filtered_owners(user).aget(pk=secret_type_id)
    except SecretType.DoesNotExist:
        raise HTTPException(status_code=404, detail="SecretType not found")
    return SecretTypePydantic.from_orm(secret_type)


@router.get("/secret_types/", response_model=SecretTypePage, tags=["Secrets"])
async def get_secret_types(
    limit: int = 10,
    offset: int = 0,
    user: User = Depends(get_request_user),
    search: Optional[str] = None,
):
    """
    List SecretTypes available to the user.
    """
    query = SecretType.filtered_owners(user).all()
    if search:
        query = query.filter(name__icontains=search)

    # Handling pagination manually for this example
    query = query[offset : offset + limit]

    # punting on async implementation of pagination until later
    return await sync_to_async(SecretTypePage.paginate)(
        output_model=SecretTypePydantic, queryset=query, limit=limit, offset=offset
    )


@router.put(
    "/secret_types/{secret_type_id}",
    response_model=SecretTypePydantic,
    tags=["Secrets"],
)
async def update_secret_type(
    secret_type_id: UUID,
    secret_type: SecretTypeEdit,
    user: User = Depends(get_request_user),
):
    try:
        secret_type_obj = await SecretType.filtered_owners(
            user, global_restricted=True
        ).aget(pk=secret_type_id)
    except SecretType.DoesNotExist:
        raise HTTPException(status_code=404, detail="SecretType not found")

    for attr, value in secret_type.model_dump().items():
        setattr(secret_type_obj, attr, value)
    await secret_type_obj.asave()
    return SecretTypePydantic.from_orm(secret_type_obj)


@router.delete("/secret_types/{secret_type_id}", tags=["Secrets"])
async def delete_secret_type(
    secret_type_id: UUID,
    user: User = Depends(get_request_user),
):
    try:
        secret_type_obj = await SecretType.filtered_owners(
            user, global_restricted=True
        ).aget(pk=secret_type_id)
    except SecretType.DoesNotExist:
        raise HTTPException(status_code=404, detail="SecretType not found")

    await secret_type_obj.adelete()
    return DeletedItem(id=str(secret_type_id))


@router.post("/secrets/", response_model=SecretPydantic, tags=["Secrets"])
async def create_secret(secret: CreateSecret, user: User = Depends(get_request_user)):
    # Record secret in database
    secret_kwargs = secret.dict(
        exclude={"id", "user_id", "value", "created_at", "updated_at"}
    )
    secret_obj = Secret(user_id=user.id, **secret_kwargs)
    await secret_obj.asave()

    # write to vault
    client = UserVaultClient(user=user)
    client.write(secret_obj.path, secret.value)

    return SecretPydantic.from_orm(secret_obj)


@router.get(
    "/secrets/{secret_id}",
    response_model=SecretPydantic,
    tags=["Secrets"],
)
async def get_secret(secret_id: UUID, user: User = Depends(get_request_user)):
    try:
        secret = await Secret.filtered_owners(user).aget(pk=secret_id)
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
    user: User = Depends(get_request_user),
):
    try:
        secret_obj = await Secret.filtered_owners(user).aget(pk=secret_id)
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
    client = UserVaultClient(user=user)
    client.write(secret_obj.path, secret.value)

    return SecretPydantic.from_orm(secret_obj)


@router.get("/secrets/", response_model=SecretPage, tags=["Secrets"])
async def get_secrets(
    path: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    user: User = Depends(get_request_user),
):
    """List endpoint used to retrieve secret metadata from the database.

    Secret values must be fetched from vault. This endpoint fetches secrets for
    use rendering choices in the UX. (e.g. to show a list of choices)
    """
    query = Secret.filtered_owners(user).all()
    if path:
        query = query.filter(path=path)

    # Handling pagination manually for this example
    query = query[offset : offset + limit]

    # punting on async implementation of pagination until later
    return await sync_to_async(SecretPage.paginate)(
        output_model=SecretPydantic, queryset=query, limit=limit, offset=offset
    )


@router.delete("/secrets/{secret_id}", response_model=DeletedItem, tags=["Secrets"])
async def delete_secret(secret_id: UUID, user: User = Depends(get_request_user)):
    try:
        secret = await Secret.filtered_owners(user).aget(pk=secret_id)
    except Secret.DoesNotExist:
        raise HTTPException(status_code=404, detail="Secret not found")

    # delete from database
    await secret.adelete()

    # update vault value
    client = UserVaultClient(user=user)
    client.delete(secret.path)

    return DeletedItem(id=str(secret_id))
