from langchain.document_loaders import (
    WebBaseLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    CSVLoader,
    UnstructuredHTMLLoader,
    BSHTMLLoader,
    JSONLoader,
)
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


BEAUTIFUL_SOUP_LOADER_CLASS_PATH = "langchain.document_loaders.BSHTMLLoader"
BEAUTIFUL_SOUP_LOADER = {
    "class_path": BEAUTIFUL_SOUP_LOADER_CLASS_PATH,
    "type": "document_loader",
    "name": "Beautiful Soup HTML Loader",
    "description": BSHTMLLoader.__doc__,
    "fields": NodeTypeField.get_fields(
        BSHTMLLoader.__init__,
        include=[
            "file_path",
            "open_encoding",
            "get_text_separator",
        ],
    ),
}


CSV_LOADER_CLASS_PATH = "langchain.document_loaders.csv_loader.CSVLoader"
CSV_LOADER = {
    "class_path": CSV_LOADER_CLASS_PATH,
    "type": "document_loader",
    "name": "CSV Loader",
    "description": CSVLoader.__doc__,
    "fields": NodeTypeField.get_fields(
        CSVLoader.__init__,
        include=[
            "file_path",
            "source_column",
            "encoding",
        ],
    ),
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


JSON_LOADER_CLASS_PATH = "langchain.document_loaders.JSONLoader"
JSON_LOADER = {
    "class_path": JSON_LOADER_CLASS_PATH,
    "type": "document_loader",
    "name": "JSON Loader",
    "description": JSONLoader.__doc__,
    "fields": NodeTypeField.get_fields(
        JSONLoader.__init__,
        include=[
            "file_path",
            "jq_schema",
            "content_key",
            "text_content",
            "json_lines",
        ],
        field_options={
            "jq_schema": {
                "input_type": "textarea",
            },
        },
    ),
}


PDF_LOADER_CLASS_PATH = "langchain.document_loaders.PyPDFLoader"
PDF_LOADER = {
    "class_path": PDF_LOADER_CLASS_PATH,
    "type": "document_loader",
    "name": "PDF Loader",
    "description": PyPDFLoader.__doc__,
    "fields": NodeTypeField.get_fields(
        PyPDFLoader.__init__,
        include=[
            "file_path",
            "password",
        ],
    ),
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


UNSTRUCTURED_HTML_LOADER_CLASS_PATH = (
    "langchain.document_loaders.UnstructuredHTMLLoader"
)
UNSTRUCTURED_HTML_LOADER = {
    "class_path": UNSTRUCTURED_HTML_LOADER_CLASS_PATH,
    "type": "document_loader",
    "name": "Unstructured HTML Loader",
    "description": UnstructuredHTMLLoader.__doc__,
    "fields": NodeTypeField.get_fields(
        UnstructuredHTMLLoader.__init__, include=["file_path" "mode"]
    ),
}


UNSTRUCTURED_MARKDOWN_LOADER_CLASS_PATH = (
    "langchain.document_loaders.UnstructuredMarkdownLoader"
)
UNSTRUCTURED_MARKDOWN_LOADER = {
    "class_path": UNSTRUCTURED_MARKDOWN_LOADER_CLASS_PATH,
    "type": "document_loader",
    "name": "Unstructured Markdown Loader",
    "description": UnstructuredMarkdownLoader.__doc__,
    "fields": NodeTypeField.get_fields(
        UnstructuredMarkdownLoader.__init__, include=["file_path" "mode"]
    ),
}


DOCUMENT_LOADERS = [
    BEAUTIFUL_SOUP_LOADER,
    CSV_LOADER,
    GENERIC_LOADER,
    JSON_LOADER,
    PDF_LOADER,
    WEB_BASE_LOADER,
    UNSTRUCTURED_HTML_LOADER,
    UNSTRUCTURED_MARKDOWN_LOADER,
]

__all__ = [
    "DOCUMENT_LOADERS",
    "BEAUTIFUL_SOUP_LOADER_CLASS_PATH",
    "CSV_LOADER_CLASS_PATH",
    "GENERIC_LOADER_CLASS_PATH",
    "JSON_LOADER_CLASS_PATH",
    "PDF_LOADER_CLASS_PATH",
    "WEB_BASE_LOADER_CLASS_PATH",
    "UNSTRUCTURED_HTML_LOADER_CLASS_PATH",
    "UNSTRUCTURED_MARKDOWN_LOADER_CLASS_PATH",
    "BEAUTIFUL_SOUP_LOADER_CLASS_PATH",
    "GENERIC_LOADER_CLASS_PATH",
]
