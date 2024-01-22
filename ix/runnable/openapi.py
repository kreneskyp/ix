import uuid
import httpx
from typing import Optional, Type, Dict, Any

from langchain_core.runnables import RunnableSerializable, RunnableConfig
from langchain_core.runnables.utils import Input, Output
from pydantic import BaseModel

from ix.data.models import Schema
from ix.utils.openapi import get_input_schema, HTTP_METHODS, get_action_schema
from jsonschema_pydantic import jsonschema_to_pydantic


def build_httpx_kwargs(path: str, input: Input, **kwargs) -> dict[str, Any]:
    """Build kwargs for OpenAPI request with httpx"""
    formatted_path = path.format(**input.get("path", {}))
    headers = kwargs.get("headers", {})
    headers.update(input.get("headers", {}))
    params = {}
    if "query" in input:
        query = input["query"]
        params = query.model_dump() if isinstance(query, BaseModel) else query
    request_kwargs = {
        "url": formatted_path,
        "params": params,
        "headers": headers,
    }

    body = input.get("body", None)
    if body:
        if isinstance(body, BaseModel):
            request_kwargs["json"] = body.model_dump()
        else:
            request_kwargs["json"] = body

    return request_kwargs


class RunOpenAPIRequest(RunnableSerializable[Input, Output]):
    """Make a request to an OpenAPI server and return the response."""

    schema_id: uuid.UUID = None
    server: str
    path: str
    method: HTTP_METHODS
    headers: Optional[dict] = None

    class Config:
        arbitrary_types_allowed = True

    def get_schema(self) -> Schema:
        return Schema.objects.get(pk=self.schema_id)

    def _get_input_schema(self, schema: Schema) -> Dict[str, Any]:
        """Get JSON schema from OpenAPI schema for the specified path and method.

        The schema includes params for path, query, and body.
        """
        if schema.type != "openapi":
            raise ValueError("Schema must be of type openapi")

        action_schema = get_action_schema(schema.value, self.path, self.method)
        input_schema = get_input_schema(action_schema, self.path, self.method)
        return input_schema

    def get_input_schema(
        self, config: Optional[RunnableConfig] = None
    ) -> Type[BaseModel]:
        """return input schema for the path and method."""
        schema = self.get_schema()
        input_schema_dict = self._get_input_schema(schema)
        input_schema = jsonschema_to_pydantic(input_schema_dict, version=2)
        return input_schema

    def get_output_schema(
        self, config: Optional[RunnableConfig] = None
    ) -> Type[BaseModel]:
        # TODO: extract from openapi spec
        return super().get_output_schema(config)

    def invoke(
        self, input: Input, config: Optional[RunnableConfig] = None, **kwargs
    ) -> Output:
        with httpx.Client() as client:
            request_kwargs = build_httpx_kwargs(self.server, self.path, input)
            client_method = getattr(client, self.method)
            response = client_method(**request_kwargs)

        if response.status_code != 200:
            raise Exception(f"Failed to get schema: {response.content}")

        return response.json()

    async def ainvoke(
        self, input: Input, config: Optional[RunnableConfig] = None, **kwargs
    ) -> Output:
        async with httpx.AsyncClient(base_url=self.server) as client:
            request_kwargs = build_httpx_kwargs(self.path, input)
            client_method = getattr(client, self.method)
            response = await client_method(**request_kwargs)

        if response.status_code != 200:
            raise Exception(f"Failed to get schema: {response.content}")

        return response.json()
