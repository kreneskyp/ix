import logging
from typing import Literal
from uuid import UUID

from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends, HTTPException

from ix.api.chains.endpoints import DeletedItem
from ix.data.models import Schema, Data
from ix.data.types import (
    Schema as SchemaPydantic,
    Data as DataPydantic,
    SchemaPage,
    DataPage,
    EditSchema,
)
from ix.ix_users.models import User
from ix.api.auth import get_request_user
from ix.utils.openapi import get_input_schema

logger = logging.getLogger(__name__)
router = APIRouter()


# Schema Endpoints
@router.post(
    "/schemas/",
    operation_id="create_schema",
    response_model=SchemaPydantic,
    tags=["Schemas"],
)
async def create_schema(schema: EditSchema, user: User = Depends(get_request_user)):
    schema_obj = await Schema.objects.acreate(user_id=user.id, **schema.model_dump())
    return SchemaPydantic.model_validate(schema_obj)


@router.get(
    "/schemas/{schema_id}",
    operation_id="get_schema",
    response_model=SchemaPydantic,
    tags=["Schemas"],
)
async def get_schema(schema_id: UUID, user: User = Depends(get_request_user)):
    try:
        schema = await Schema.filtered_owners(user).aget(pk=schema_id)
    except Schema.DoesNotExist:
        raise HTTPException(status_code=404, detail="Schema not found")
    return SchemaPydantic.model_validate(schema)


@router.get(
    "/schemas/", operation_id="get_schemas", response_model=SchemaPage, tags=["Schemas"]
)
async def get_schemas(
    limit: int = 10,
    offset: int = 0,
    type: Literal["openapi", "json"] = "json",
    user: User = Depends(get_request_user),
):
    query = Schema.filtered_owners(user)
    if type:
        query = query.filter(type=type)

    # punting on async implementation of pagination until later
    return await sync_to_async(SchemaPage.paginate)(
        output_model=SchemaPydantic, queryset=query, limit=limit, offset=offset
    )


@router.put(
    "/schemas/{schema_id}",
    operation_id="update_schema",
    response_model=SchemaPydantic,
    tags=["Schemas"],
)
async def update_schema(
    schema_id: UUID, schema_data: EditSchema, user: User = Depends(get_request_user)
):
    try:
        schema_obj = await Schema.filtered_owners(user).aget(pk=schema_id)
    except Schema.DoesNotExist:
        raise HTTPException(status_code=404, detail="Schema not found")

    for attr, value in schema_data.model_dump().items():
        setattr(schema_obj, attr, value)
    await schema_obj.asave()
    return SchemaPydantic.model_validate(schema_obj)


@router.delete("/schemas/{schema_id}", operation_id="delete_schema", tags=["Schemas"])
async def delete_schema(schema_id: UUID, user: User = Depends(get_request_user)):
    try:
        schema = await Schema.filtered_owners(user).aget(pk=schema_id)
    except Schema.DoesNotExist:
        raise HTTPException(status_code=404, detail="Schema not found")

    await schema.adelete()
    return DeletedItem(id=str(schema_id))


@router.get(
    "/schemas/{schema_id}/action", operation_id="get_schema_action", tags=["Schemas"]
)
async def get_schema_action(
    schema_id: UUID, path: str, method: str, user: User = Depends(get_request_user)
):
    try:
        schema = await Schema.filtered_owners(user).aget(pk=schema_id)
    except Schema.DoesNotExist:
        raise HTTPException(status_code=404, detail="Schema not found")

    return get_input_schema(schema.value, path, method)


# Data Endpoints
@router.post(
    "/data/", response_model=DataPydantic, operation_id="create_data", tags=["Data"]
)
async def create_data(data: DataPydantic, user: User = Depends(get_request_user)):
    data_obj = await Data.objects.acreate(user_id=user.id, **data.model_dump())
    return DataPydantic.model_validate(data_obj)


@router.get("/data/", response_model=DataPage, operation_id="get_datas", tags=["Data"])
async def get_datas(
    limit: int = 10,
    offset: int = 0,
    user: User = Depends(get_request_user),
):
    query = Data.filtered_owners(user)

    # punting on async implementation of pagination until later
    return await sync_to_async(DataPage.paginate)(
        output_model=DataPydantic, queryset=query, limit=limit, offset=offset
    )


@router.get(
    "/data/{data_id}",
    operation_id="get_data",
    response_model=DataPydantic,
    tags=["Data"],
)
async def get_data(data_id: UUID, user: User = Depends(get_request_user)):
    try:
        data = await Data.filtered_owners(user).aget(pk=data_id)
    except Data.DoesNotExist:
        raise HTTPException(status_code=404, detail="Data not found")
    return DataPydantic.model_validate(data)


@router.put(
    "/data/{data_id}",
    operation_id="update_data",
    response_model=DataPydantic,
    tags=["Data"],
)
async def update_data(
    data_id: UUID, data_data: DataPydantic, user: User = Depends(get_request_user)
):
    try:
        data_obj = await Data.filtered_owners(user).aget(pk=data_id)
    except Data.DoesNotExist:
        raise HTTPException(status_code=404, detail="Data not found")

    for attr, value in data_data.model_dump().items():
        setattr(data_obj, attr, value)
    await data_obj.asave()
    return DataPydantic.model_validate(data_obj)


@router.delete("/data/{data_id}", operation_id="delete_data", tags=["Data"])
async def delete_data(data_id: UUID, user: User = Depends(get_request_user)):
    try:
        data = await Data.filtered_owners(user).aget(pk=data_id)
    except Data.DoesNotExist:
        raise HTTPException(status_code=404, detail="Data not found")

    await data.adelete()
    return DeletedItem(id=str(data_id))
