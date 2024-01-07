import pytest
from langchain_community.document_loaders import (
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredODTLoader,
    UnstructuredPDFLoader,
    UnstructuredCSVLoader,
    UnstructuredExcelLoader,
    UnstructuredTSVLoader,
    UnstructuredPowerPointLoader,
    UnstructuredOrgModeLoader,
    UnstructuredRTFLoader,
    UnstructuredEmailLoader,
    UnstructuredImageLoader,
    UnstructuredXMLLoader,
    UnstructuredEPubLoader,
    UnstructuredRSTLoader,
)

from ix.chains.fixture_src.unstructured import (
    UNSTRUCTURED_HTML_LOADER_CLASS_PATH,
    UNSTRUCTURED_MARKDOWN_LOADER_CLASS_PATH,
    UNSTRUCTURED_WORD_DOCUMENT_LOADER_CLASS_PATH,
    UNSTRUCTURED_ODT_LOADER_CLASS_PATH,
    UNSTRUCTURED_PDF_LOADER_CLASS_PATH,
    UNSTRUCTURED_CSV_LOADER_CLASS_PATH,
    UNSTRUCTURED_TSV_LOADER_CLASS_PATH,
    UNSTRUCTURED_EXCEL_LOADER_CLASS_PATH,
    UNSTRUCTURED_POWERPOINT_LOADER_CLASS_PATH,
    UNSTRUCTURED_ORG_MODE_LOADER_CLASS_PATH,
    UNSTRUCTURED_RTF_LOADER_CLASS_PATH,
    UNSTRUCTURED_EMAIL_LOADER_CLASS_PATH,
    UNSTRUCTURED_IMAGE_LOADER_CLASS_PATH,
    UNSTRUCTURED_XML_LOADER_CLASS_PATH,
    UNSTRUCTURED_EPUB_LOADER_CLASS_PATH,
    UNSTRUCTURED_RST_LOADER_CLASS_PATH,
)
from ix.chains.tests.components.test_document_loaders import (
    TEST_HTML_FILE_PATH,
    TEST_MARKDOWN_FILE_PATH,
    TEST_PDF_FILE_PATH,
    TEST_CSV_FILE_PATH,
)
from ix.chains.tests.test_config_loader import unpack_chain_flow
from ix.runnable.documents import RunLoader


@pytest.mark.django_db
class TestUnstructuredAPILoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_HTML_LOADER_CLASS_PATH,
        "config": {
            "url": "MOCK_URL",
            "api_key": "MOCK_API_KEY",
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredHTMLLoader


@pytest.mark.django_db
class TestUnstructuredHTMLLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_HTML_LOADER_CLASS_PATH,
        "config": {
            "file_path": [TEST_HTML_FILE_PATH],
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredHTMLLoader


@pytest.mark.django_db
class TestUnstructuredMarkdownLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_MARKDOWN_LOADER_CLASS_PATH,
        "config": {"file_path": [TEST_MARKDOWN_FILE_PATH], "mode": ""},
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredMarkdownLoader


@pytest.mark.django_db
class TestUnstructuredWordDocumentLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_WORD_DOCUMENT_LOADER_CLASS_PATH,
        "config": {
            "file_path": ["MOCK_PATH"],
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredWordDocumentLoader


@pytest.mark.django_db
class TestUnstructuredODTLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_ODT_LOADER_CLASS_PATH,
        "config": {
            "file_path": ["MOCK_PATH"],
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredODTLoader


@pytest.mark.django_db
class TestUnstructuredPDFLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_PDF_LOADER_CLASS_PATH,
        "config": {
            "file_path": [TEST_PDF_FILE_PATH],
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredPDFLoader


@pytest.mark.django_db
class TestUnstructuredCSVLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_CSV_LOADER_CLASS_PATH,
        "config": {
            "file_path": [TEST_CSV_FILE_PATH],
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredCSVLoader


@pytest.mark.django_db
class TestUnstructuredRSTLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_RST_LOADER_CLASS_PATH,
        "config": {
            "file_path": ["MOCK_FILE_PATH"],
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredRSTLoader


@pytest.mark.django_db
class TestUnstructuredEPubLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_EPUB_LOADER_CLASS_PATH,
        "config": {
            "file_path": ["MOCK_FILE_PATH"],
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredEPubLoader


@pytest.mark.django_db
class TestUnstructuredXMLLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_XML_LOADER_CLASS_PATH,
        "config": {
            "file_path": ["MOCK_FILE_PATH"],
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredXMLLoader


@pytest.mark.django_db
class TestUnstructuredImageLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_IMAGE_LOADER_CLASS_PATH,
        "config": {
            "file_path": ["MOCK_FILE_PATH"],
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredImageLoader


@pytest.mark.django_db
class TestUnstructuredEmailLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_EMAIL_LOADER_CLASS_PATH,
        "config": {
            "file_path": ["MOCK_FILE_PATH"],
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredEmailLoader


@pytest.mark.django_db
class TestUnstructuredRTFLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_RTF_LOADER_CLASS_PATH,
        "config": {
            "file_path": ["MOCK_FILE_PATH"],
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredRTFLoader


@pytest.mark.django_db
class TestUnstructuredOrgModeLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_ORG_MODE_LOADER_CLASS_PATH,
        "config": {
            "file_path": ["MOCK_FILE_PATH"],
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredOrgModeLoader


@pytest.mark.django_db
class TestUnstructuredPowerPointLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_POWERPOINT_LOADER_CLASS_PATH,
        "config": {
            "file_path": ["MOCK_FILE_PATH"],
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredPowerPointLoader


@pytest.mark.django_db
class TestUnstructuredExcelLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_EXCEL_LOADER_CLASS_PATH,
        "config": {
            "file_path": ["MOCK_FILE_PATH"],
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredExcelLoader


@pytest.mark.django_db
class TestUnstructuredTSVLoader:
    CONFIG = {
        "class_path": UNSTRUCTURED_TSV_LOADER_CLASS_PATH,
        "config": {
            "file_path": ["MOCK_FILE_PATH"],
        },
    }

    async def test_load(self, aload_chain):
        component = await aload_chain(self.CONFIG)
        component = unpack_chain_flow(component)
        assert isinstance(component, RunLoader)
        assert component.initializer is UnstructuredTSVLoader
