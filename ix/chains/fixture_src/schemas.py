from ix.api.components.types import NodeType, NodeTypeField, Connector
from ix.runnable.schema import SaveSchema, FunctionSchema

FUNCTION_SCHEMA_CLASS_PATH = "ix.runnable.schema.FunctionSchema"
FUNCTION_SCHEMA = NodeType(
    class_path=FUNCTION_SCHEMA_CLASS_PATH,
    name="Function Schema",
    description="Returns a statically defined Open AI function schema.",
    type="schema",
    connectors=[
        Connector(key="out", label="Schema", type="source", source_type="schema"),
    ],
    fields=NodeTypeField.get_fields(
        FunctionSchema,
        include=["name", "description", "parameters"],
        field_options={
            "parameters": {
                "input_type": "textarea",
            }
        },
    ),
)


LOAD_SCHEMA_CLASS_PATH = "ix.runnable.schema.LoadSchema"
LOAD_SCHEMA = NodeType(
    class_path=LOAD_SCHEMA_CLASS_PATH,
    type="chain",
    name="Load Schema",
    description="Get a schema from the schema registry",
    connectors=[
        Connector(key="out", label="Schema", type="source", source_type="schema"),
    ],
    fields=[
        NodeTypeField(
            name="schema_id",
            label="Schema",
            type="str",
            description="Schema to load from the registry.",
            required=True,
            input_type="IX:json_schema",
        )
    ],
)

SAVE_SCHEMA_CLASS_PATH = "ix.runnable.schema.SaveSchema"
SAVE_SCHEMA = NodeType(
    class_path=SAVE_SCHEMA_CLASS_PATH,
    type="chain",
    name="Save Schema",
    description="Save a schema to the schema registry",
    fields=NodeTypeField.get_fields(SaveSchema, include=[]),
)


SCHEMAS = [
    FUNCTION_SCHEMA,
    LOAD_SCHEMA,
    SAVE_SCHEMA,
]
