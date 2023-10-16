import asyncio
from asgiref.sync import sync_to_async
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
import httpx
from ix.langservers.models import LangServer
from ix.api.auth import get_request_user
from ix.api.chains.endpoints import DeletedItem
from ix.api.langservers.types import (
    LangServer as LangServerPydantic,
    LangServerPage,
    RemoteRunnableConfig,
    LangServerImport,
    LangServerCreateUpdate,
    LangServerConfig,
)


__all__ = ["router", "LangServerCreateUpdate"]


router = APIRouter()


@router.post("/langservers/", response_model=LangServerPydantic, tags=["LangServers"])
async def create_langserver(
    langserver: LangServerCreateUpdate, user: AbstractUser = Depends(get_request_user)
):
    langserver_obj = await LangServer.objects.acreate(user=user, **langserver.dict())
    return LangServerPydantic.from_orm(langserver_obj)


@router.post(
    "/import_langserver/", response_model=LangServerConfig, tags=["LangServers"]
)
async def import_langserver(
    langserver: LangServerImport, user: AbstractUser = Depends(get_request_user)
):
    """
    Imports a LangServer from the given endpoint and returns the metadata for it's invokable routes.
    This is a helper used to fetch the metadata for a LangServer before saving it to the database.
    """

    url = langserver.url
    if url.endswith("/"):
        url = url[:-1]

    async with httpx.AsyncClient() as client:
        openapi_url = f"{url}/openapi.json"
        response = await client.get(openapi_url)
        response.raise_for_status()
        spec = response.json()

        # get basic metadata
        name = spec["info"]["title"]
        description = spec["info"]["description"]

        # get list of remote runnable routes
        routes = []
        for path, path_data in spec["paths"].items():
            if path.endswith("/invoke"):
                route_name = path.split("/")[-2]

                # fetch input and output schemas for the route
                input_schema_url = f"{url}/{route_name}/input_schema"
                output_schema_url = f"{url}/{route_name}/output_schema"
                config_schema_url = f"{url}/{route_name}/config_schema"
                input_schema, output_schema, config_schema = await asyncio.gather(
                    client.get(input_schema_url),
                    client.get(output_schema_url),
                    client.get(config_schema_url),
                )

                routes.append(
                    RemoteRunnableConfig(
                        name=route_name,
                        input_schema=input_schema.json(),
                        output_schema=output_schema.json(),
                        config_schema=config_schema.json(),
                    )
                )

        return LangServerConfig(
            name=name, description=description, url=url, routes=routes
        )


@router.get(
    "/langservers/{langserver_id}",
    response_model=LangServerPydantic,
    tags=["LangServers"],
)
async def get_langserver(
    langserver_id: str, user: AbstractUser = Depends(get_request_user)
):
    try:
        query = LangServer.objects.filter(pk=langserver_id)
        langserver = await LangServer.filter_owners(user, query).aget()
    except LangServer.DoesNotExist:
        raise HTTPException(status_code=404, detail="LangServer not found")
    return LangServerPydantic.from_orm(langserver)


@router.get("/langservers/", response_model=LangServerPage, tags=["LangServers"])
async def get_langservers(
    search: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    user: AbstractUser = Depends(get_request_user),
):
    query = LangServer.objects.filter().order_by("name")
    query = LangServer.filter_owners(user, query)
    if search:
        query = query.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    # punting on async implementation of pagination until later
    return await sync_to_async(LangServerPage.paginate)(
        output_model=LangServerPydantic, queryset=query, limit=limit, offset=offset
    )


@router.put(
    "/langservers/{langserver_id}",
    response_model=LangServerPydantic,
    tags=["LangServers"],
)
async def update_langservers(
    langserver_id: str,
    langserver: LangServerCreateUpdate,
    user: AbstractUser = Depends(get_request_user),
):
    try:
        query = LangServer.objects.filter(pk=langserver_id)
        langserver_obj = await LangServer.filter_owners(user, query).aget()
    except LangServer.DoesNotExist:
        raise HTTPException(status_code=404, detail="LangServer not found")
    for attr, value in langserver.dict().items():
        setattr(langserver_obj, attr, value)
    await langserver_obj.asave()
    return langserver_obj


@router.delete(
    "/langservers/{langserver_id}", response_model=DeletedItem, tags=["LangServers"]
)
async def delete_langserver(
    langserver_id: str, user: AbstractUser = Depends(get_request_user)
):
    try:
        query = LangServer.objects.filter(pk=langserver_id)
        langserver = await LangServer.filter_owners(user, query).aget()
    except LangServer.DoesNotExist:
        raise HTTPException(status_code=404, detail="LangServer not found")
    await langserver.adelete()
    return DeletedItem(id=langserver_id)
