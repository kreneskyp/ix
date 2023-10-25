from uuid import UUID

from django.contrib.auth.models import AbstractUser
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
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
from ix.ix_users.models import User
from ix.utils.pydantic import create_args_model

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
    return SecretTypePydantic.model_validate(secret_type_obj)


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
    return SecretTypePydantic.model_validate(secret_type)


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
    return SecretTypePydantic.model_validate(secret_type_obj)


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


def create_secret_type_schema(fields: List[str]):
    """
    Create a JSONSchema for a SecretType from a list of fields
    """
    schema_model = create_args_model(fields)
    return schema_model.schema()


async def create_secret_type_for_data(
    user: AbstractUser, secret: CreateSecret | UpdateSecret
) -> SecretType:
    fields_schema = create_secret_type_schema(secret.value.keys())
    return await SecretType.objects.acreate(
        name=secret.type_key, user=user, fields_schema=fields_schema
    )


async def validate_secret_type(secret: CreateSecret, user: AbstractUser):
    """
    Validate that the secret value matches the secret type
    """
    if not secret.type_id:
        # embedded type creation
        secret_type = await create_secret_type_for_data(user, secret)
        type_id = secret_type.id
    else:
        # validate user can access type
        SecretType.filtered_owners(user).filter(pk=secret.type_id).aget()
        if (
            not await SecretType.filtered_owners(user)
            .filter(pk=secret.type_id)
            .aexists()
        ):
            raise HTTPException(status_code=422, detail="Invalid secret type")
        type_id = secret.type_id
    return type_id


@router.post("/secrets/", response_model=SecretPydantic, tags=["Secrets"])
async def create_secret(secret: CreateSecret, user: User = Depends(get_request_user)):
    type_id = await validate_secret_type(secret, user)

    # Record secret in database
    secret_kwargs = secret.model_dump(
        exclude={
            "id",
            "user_id",
            "value",
            "created_at",
            "updated_at",
            "type_id",
            "type_key",
        }
    )
    secret_obj = Secret(user_id=user.id, type_id=type_id, **secret_kwargs)
    await secret_obj.asave()

    # write to vault
    await secret_obj.write(secret.value)

    return SecretPydantic.model_validate(secret_obj)


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
    return SecretPydantic.model_validate(secret)


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

    secret_kwargs = secret.model_dump(
        exclude={
            "id",
            "user_id",
            "group_id",
            "value",
            "created_at",
            "updated_at",
            "type_id",
            "type_key",
        }
    )

    # update DB if needed
    has_db_update = False
    for attr, value in secret_kwargs.items():
        if hasattr(secret_obj, attr) and getattr(secret_obj, attr) != value:
            setattr(secret_obj, attr, value)
            has_db_update = True
    if has_db_update:
        await secret_obj.asave()

    # set user on secret to avoid extra query
    secret_obj.user = user

    # update vault value
    if secret.value:
        current_value = await secret_obj.read()
        if current_value != secret.value:
            current_value.update(secret.value)
            await secret_obj.write(current_value)

    return SecretPydantic.model_validate(secret_obj)


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

    # set user on secret to avoid extra query
    secret.user = user

    # delete vault and database
    await secret.delete_secure()
    await secret.adelete()

    return DeletedItem(id=str(secret_id))
