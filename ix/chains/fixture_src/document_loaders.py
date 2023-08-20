from langchain.document_loaders.generic import GenericLoader

from ix.api.chains.types import NodeTypeField
from ix.chains.fixture_src.targets import PARSER_TARGET


FILE_SUFFIXES_FIELD = {
    "default": None,
    "label": "Suffixes",
    "name": "suffixes",
    "required": False,
    "type": "list",
}

PATH_FIELD = {
    "label": "Path",
    "name": "path",
    "required": True,
    "type": "str",
    "style": {"width": "100%"},
}


GENERIC_LOADER_CLASS_PATH = (
    "langchain.document_loaders.generic.GenericLoader.from_filesystem"
)
GENERIC_LOADER = {
    "class_path": GENERIC_LOADER_CLASS_PATH,
    "type": "document_loader",
    "name": "Filesystem Loader",
    "description": "Load documents from the filesystem.",
    "fields": [PATH_FIELD, FILE_SUFFIXES_FIELD]
    + NodeTypeField.get_fields_from_method(
        GenericLoader.from_filesystem,
        include=[
            "glob",
        ],
    ),
    "connectors": [PARSER_TARGET],
}

DOCUMENT_LOADERS = [GENERIC_LOADER]

__all__ = ["DOCUMENT_LOADERS", "GENERIC_LOADER_CLASS_PATH"]
