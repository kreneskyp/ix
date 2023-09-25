from asgiref.sync import sync_to_async
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from uuid import UUID

from ix.api.auth import get_request_user
from ix.datasources.models import DataSource
from ix.api.chains.endpoints import DeletedItem
from pydantic import BaseModel
from ix.api.datasources.types import DataSource as DataSourcePydantic, DataSourcePage


router = APIRouter()


class DataSourceCreateUpdate(BaseModel):
    name: str
    description: str
    config: dict
    retrieval_chain: UUID


@router.post("/datasources/", response_model=DataSourcePydantic, tags=["DataSources"])
async def create_datasource(
    datasource: DataSourceCreateUpdate,
    current_user: AbstractUser = Depends(get_request_user),
):
    # Assign the user_id to the created datasource
    datasource_dict = datasource.dict()
    datasource_dict["user_id"] = current_user.id

    datasource_obj = DataSource(**datasource_dict)
    await datasource_obj.save()
    return DataSourcePydantic.from_orm(datasource_obj)


@router.get(
    "/datasources/{datasource_id}",
    response_model=DataSourcePydantic,
    tags=["DataSources"],
)
async def get_datasource(
    datasource_id: UUID,
    current_user: AbstractUser = Depends(get_request_user),  # Get the current user
):
    try:
        datasource = await DataSource.objects.get(
            pk=datasource_id, user_id=current_user.id
        )
    except DataSource.DoesNotExist:
        raise HTTPException(status_code=404, detail="DataSource not found")
    return DataSourcePydantic.from_orm(datasource)


@router.get("/datasources/", response_model=DataSourcePage, tags=["DataSources"])
async def get_datasources(
    search: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    current_user: AbstractUser = Depends(get_request_user),  # Get the current user
):
    query = DataSource.objects.filter(user_id=current_user.id)
    if search:
        query = query.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    # punting on async implementation of pagination until later
    return await sync_to_async(DataSourcePage.paginate)(
        output_model=DataSourcePydantic, queryset=query, limit=limit, offset=offset
    )


@router.put(
    "/datasources/{datasource_id}",
    response_model=DataSourcePydantic,
    tags=["DataSources"],
)
async def update_datasource(
    datasource_id: UUID,
    datasource: DataSourceCreateUpdate,
    current_user: AbstractUser = Depends(get_request_user),  # Get the current user
):
    try:
        datasource_obj = await DataSource.objects.get(
            pk=datasource_id, user_id=current_user.id
        )
    except DataSource.DoesNotExist:
        raise HTTPException(status_code=404, detail="DataSource not found")

    for attr, value in datasource.dict().items():
        setattr(datasource_obj, attr, value)

    await datasource_obj.save()
    return DataSourcePydantic.from_orm(datasource_obj)


@router.delete(
    "/datasources/{datasource_id}", response_model=DeletedItem, tags=["DataSources"]
)
async def delete_datasource(
    datasource_id: UUID,
    current_user: AbstractUser = Depends(get_request_user),  # Get the current user
):
    try:
        datasource = await DataSource.objects.get(
            pk=datasource_id, user_id=current_user.id
        )
    except DataSource.DoesNotExist:
        raise HTTPException(status_code=404, detail="DataSource not found")

    await datasource.delete()
    return DeletedItem(id=str(datasource_id))
