import traceback

from django.conf import settings
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from ix.api.agents.endpoints import router as agents_router
from ix.api.artifacts.endpoints import router as artifacts_router
from ix.api.components.endpoints import router as components_router
from ix.api.chains.endpoints import router as chains_router
from ix.api.editor.endpoints import router as editor_router
from ix.api.chats.endpoints import router as chats_router
from ix.api.datasources.endpoints import router as datasources_router
from ix.api.secrets.endpoints import router as secrets_router
from ix.api.workspace.endpoints import router as workspace_router
from ix.data.endpoints import router as data_router


from ix.runnable_log.endpoints import router as runnable_log_router

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
app.include_router(data_router)
app.include_router(datasources_router)
app.include_router(secrets_router)
app.include_router(workspace_router)
app.include_router(runnable_log_router)


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


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    error_message = str(exc)
    error_message_lines = error_message.splitlines()

    # Check if settings.DEBUG is True before including the traceback
    if settings.DEBUG:
        traceback_info = traceback.format_exc()
        traceback_lines = traceback_info.splitlines()
    else:
        traceback_lines = []

    # Create a JSON object with separate fields for error message and traceback
    error_response = {
        "error_message": error_message_lines,
        "traceback": traceback_lines,
    }

    # Return a JSON response with the error response object and a 500 status code
    response = JSONResponse(status_code=500, content=error_response)

    # Set the content type
    response.headers["Content-Type"] = "application/json; charset=utf-8"

    return response
