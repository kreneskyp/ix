from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from ix.api.agents.endpoints import router as agents_router
from ix.api.artifacts.endpoints import router as artifacts_router
from ix.api.components.endpoints import router as components_router
from ix.api.chains.endpoints import router as chains_router
from ix.api.editor.endpoints import router as editor_router
from ix.api.chats.endpoints import router as chats_router
from ix.api.datasources.endpoints import router as datasources_router

app = FastAPI(
    title="IX agent editor API",
    description="API for editing Agents, Chains, and node_type components",
)
app.include_router(components_router)
app.include_router(chains_router)
app.include_router(agents_router)
app.include_router(chats_router)
app.include_router(artifacts_router)
app.include_router(editor_router)
app.include_router(datasources_router)


def custom_openapi():
    """
    This function overrides the default OpenAPI schema generation.

    Servers:
    Servers is limited to just the internally accessible development server.
    This is needed for OpenAPI chain to work. The chain does not include the
    protocol and hostname unless it is in the server url. The default
    server is returned as /api

    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["servers"] = [
        {"url": "http://172.17.0.1:8000/api", "description": "Development server"},
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
