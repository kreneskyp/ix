from langchain.agents.agent_toolkits import FileManagementToolkit
from ix.api.chains.types import NodeTypeField


FILE_MANAGEMENT_TOOLKIT_CLASS_PATH = (
    "langchain.agents.agent_toolkits.file_management.toolkit.FileManagementToolkit"
)
FILE_MANAGEMENT_TOOLKIT = {
    "class_path": FILE_MANAGEMENT_TOOLKIT_CLASS_PATH,
    "type": "toolkit",
    "name": "File Management",
    "description": "Toolkit for interacting with a Local Files.",
    "fields": NodeTypeField.get_fields(
        FileManagementToolkit,
        include=["root_dir"],
        field_options={
            "root_dir": {
                "default": "/var/app/workdir",
            }
        },
    ),
}


TOOLKITS = [FILE_MANAGEMENT_TOOLKIT]
