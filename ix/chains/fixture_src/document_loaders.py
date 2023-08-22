from langchain.document_loaders import WebBaseLoader
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
    + NodeTypeField.get_fields(
        GenericLoader.from_filesystem,
        include=[
            "glob",
        ],
    ),
    "connectors": [PARSER_TARGET],
}


WEB_BASE_LOADER_CLASS_PATH = "langchain.document_loaders.web_base.WebBaseLoader"
WEB_BASE_LOADER = {
    "class_path": WEB_BASE_LOADER_CLASS_PATH,
    "type": "document_loader",
    "name": "Web Loader",
    "description": "Load documents from the web and parse them with BeautifulSoup.",
    "connectors": [PARSER_TARGET],
    "fields": [
        {
            "name": "web_path",
            "type": "list",
            "description": "URL(s) of the web page",
            "style": {"width": "100%"},
        }
    ]
    + NodeTypeField.get_fields(
        WebBaseLoader.__init__,
        include=[
            "verify_ssl",
            "continue_on_failure",
        ],
    ),
}


DOCUMENT_LOADERS = [GENERIC_LOADER, WEB_BASE_LOADER]

__all__ = ["DOCUMENT_LOADERS", "GENERIC_LOADER_CLASS_PATH"]
