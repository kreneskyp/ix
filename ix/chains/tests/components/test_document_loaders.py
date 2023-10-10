import json

import pytest
from langchain.document_loaders import (
    UnstructuredMarkdownLoader,
    UnstructuredHTMLLoader,
    PyPDFLoader,
    JSONLoader,
    CSVLoader,
    BSHTMLLoader,
)

from ix.chains.fixture_src.document_loaders import (
    BEAUTIFUL_SOUP_LOADER_CLASS_PATH,
    CSV_LOADER_CLASS_PATH,
    PDF_LOADER_CLASS_PATH,
    UNSTRUCTURED_HTML_LOADER_CLASS_PATH,
    UNSTRUCTURED_MARKDOWN_LOADER_CLASS_PATH,
    JSON_LOADER_CLASS_PATH,
)


TEST_HTML_FILE_PATH = "/var/app/test_data/documents/test.html"
TEST_CSV_FILE_PATH = "/var/app/test_data/documents/test.csv"
TEST_JSON_FILE_PATH = "/var/app/test_data/documents/test.json"
TEST_PDF_FILE_PATH = "/var/app/test_data/documents/test.pdf"
TEST_MARKDOWN_FILE_PATH = "/var/app/test_data/documents/README.md"


BEAUTIFUL_SOUP_LOADER = {
    "class_path": BEAUTIFUL_SOUP_LOADER_CLASS_PATH,
    "config": {
        "file_path": TEST_HTML_FILE_PATH,
    },
}

CSV_LOADER = {
    "class_path": CSV_LOADER_CLASS_PATH,
    "config": {
        "file_path": TEST_CSV_FILE_PATH,
    },
}

JQ_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"},
        "email": {"type": "string", "format": "email"},
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"},
                "country": {"type": "string"},
            },
            "required": ["street", "city", "country"],
        },
        "hobbies": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["name", "age", "email", "address", "hobbies"],
}


JSON_LOADER = {
    "class_path": JSON_LOADER_CLASS_PATH,
    "config": {
        "file_path": TEST_JSON_FILE_PATH,
        "jq_schema": json.dumps(JQ_SCHEMA),
    },
}

PDF_LOADER = {
    "class_path": PDF_LOADER_CLASS_PATH,
    "config": {
        "file_path": TEST_PDF_FILE_PATH,
    },
}

UNSTRUCTURED_HTML_LOADER = {
    "class_path": UNSTRUCTURED_HTML_LOADER_CLASS_PATH,
    "config": {
        "file_path": TEST_HTML_FILE_PATH,
    },
}

UNSTRUCTURED_MARKDOWN_LOADER = {
    "class_path": UNSTRUCTURED_MARKDOWN_LOADER_CLASS_PATH,
    "config": {
        "file_path": TEST_MARKDOWN_FILE_PATH,
    },
}


@pytest.mark.django_db
class TestBeautifulSoupLoader:
    async def test_load(self, aload_chain):
        component = await aload_chain(BEAUTIFUL_SOUP_LOADER)
        assert isinstance(component, BSHTMLLoader)


@pytest.mark.django_db
class TestCSVLoader:
    async def test_load(self, aload_chain):
        component = await aload_chain(CSV_LOADER)
        assert isinstance(component, CSVLoader)


@pytest.mark.django_db
class TestJSONLoader:
    async def test_load(self, aload_chain):
        component = await aload_chain(JSON_LOADER)
        assert isinstance(component, JSONLoader)


@pytest.mark.django_db
class TestPDFLoader:
    async def test_load(self, aload_chain):
        component = await aload_chain(PDF_LOADER)
        assert isinstance(component, PyPDFLoader)


@pytest.mark.django_db
class TestUnstructuredHTMLLoader:
    async def test_load(self, aload_chain):
        component = await aload_chain(UNSTRUCTURED_HTML_LOADER)
        assert isinstance(component, UnstructuredHTMLLoader)


@pytest.mark.django_db
class TestUnstructuredMarkdownLoader:
    async def test_load(self, aload_chain):
        component = await aload_chain(UNSTRUCTURED_MARKDOWN_LOADER)
        assert isinstance(component, UnstructuredMarkdownLoader)
