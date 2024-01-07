import logging
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
from ix.secrets.models import SecretType, Secret, MissingSecret
from ix.ix_users.models import User
from ix.utils.pydantic import create_args_model

logger = logging.getLogger(__name__)
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
    key: Optional[str] = None,
):
    """
    List SecretTypes available to the user.
    """
    query = SecretType.filtered_owners(user).all()
    if search:
        query = query.filter(name__icontains=search)
    if key:
        query = query.filter(name=key)

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


async def validate_secret_type(secret: CreateSecret, user: AbstractUser) -> SecretType:
    """
    Validate that the secret value matches the secret type
    """
    if not secret.type_id:
        # embedded type creation
        return await create_secret_type_for_data(user, secret)
    else:
        # validate user can access type
        try:
            return await SecretType.filtered_owners(user).aget(pk=secret.type_id)
        except SecretType.DoesNotExist:
            raise HTTPException(status_code=422, detail="Invalid secret type")


@router.post("/secrets/", response_model=SecretPydantic, tags=["Secrets"])
async def create_secret(secret: CreateSecret, user: User = Depends(get_request_user)):
    secret_type = await validate_secret_type(secret, user)

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
    secret_obj = Secret(user_id=user.id, type=secret_type, **secret_kwargs)
    await secret_obj.asave()

    # write to vault
    await secret_obj.awrite(secret.value)

    return SecretPydantic.model_validate(secret_obj)


@router.get(
    "/secrets/{secret_id}",
    response_model=SecretPydantic,
    tags=["Secrets"],
)
async def get_secret(secret_id: UUID, user: User = Depends(get_request_user)):
    try:
        secret_obj = await Secret.filtered_owners(user).aget(pk=secret_id)
    except Secret.DoesNotExist:
        raise HTTPException(status_code=404, detail="Secret not found")

    # fetch secret type manually to avoid async weirdness
    secret_obj.type = await SecretType.objects.aget(pk=secret_obj.type_id)

    return SecretPydantic.model_validate(secret_obj)


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
        try:
            current_value = await secret_obj.aread()
        except MissingSecret:
            current_value = {}
        if current_value != secret.value:
            current_value.update(secret.value)
            await secret_obj.awrite(current_value)

    # fetch secret type manually to avoid async weirdness
    secret_obj.type = await SecretType.objects.aget(pk=secret_obj.type_id)

    return SecretPydantic.model_validate(secret_obj)


@router.get("/secrets/", response_model=SecretPage, tags=["Secrets"])
async def get_secrets(
    secret_type: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    user: User = Depends(get_request_user),
):
    """List endpoint used to retrieve secret metadata from the database.

    Secret values must be fetched from vault. This endpoint fetches secrets for
    use rendering choices in the UX. (e.g. to show a list of choices)
    """
    query = Secret.filtered_owners(user).all()
    if secret_type:
        query = query.filter(type__name=secret_type)

    # Handling pagination manually for this example
    query = query[offset : offset + limit]

    # punting on async implementation of pagination until later
    # will need to handle select_related async as well
    query.select_related("type")
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
    try:
        await secret.adelete_secure()
    except MissingSecret:
        logger.warning(f"Secret {secret_id} not found in vault when deleting")
    await secret.adelete()

    return DeletedItem(id=str(secret_id))
