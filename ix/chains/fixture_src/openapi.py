from ix.api.components.types import NodeType, NodeTypeField, DisplayGroup
from ix.runnable.openapi import RunOpenAPIRequest

RUN_OPEN_API_REQUEST_CLASS_PATH = "ix.runnable.openapi.RunOpenAPIRequest"
RUN_OPEN_API_REQUEST = NodeType(
    class_path=RUN_OPEN_API_REQUEST_CLASS_PATH,
    type="chain",
    name="OpenAPI Request",
    description="Send a request to an OpenAPI server",
    fields=NodeTypeField.get_fields(
        RunOpenAPIRequest,
        include=[
            "schema_id",
            "server",
            "path",
            "method",
            "headers",
        ],
        field_options={
            "schema_id": {"label": "Schema", "input_type": "IX:openapi_schema"},
            "server": {"input_type": "IX:openapi_server"},
            "path": {"label": "Action", "input_type": "IX:openapi_action"},
            "method": {"input_type": "hidden"},
        },
    ),
    display_groups=[
        DisplayGroup(
            key="Config",
            label="Config",
            fields=["schema_id", "server", "path", "method"],
        ),
        DisplayGroup(key="Auth", label="Authentication", fields=["headers"]),
    ],
)


OPEN_API = [RUN_OPEN_API_REQUEST]
