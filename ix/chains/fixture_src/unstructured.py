from langchain_community.document_loaders import (
    UnstructuredFileIOLoader,
    UnstructuredAPIFileLoader,
    UnstructuredHTMLLoader,
)

from ix.api.components.types import NodeTypeField, NodeType
from ix.chains.fixture_src.document_loaders import LOADER_CONNECTORS

FILE_PATH_LIST = NodeTypeField(
    name="file_path",
    type="list",
    required=True,
    description="List of file paths",
)
UNSTRUCTURED_IO_MODE = NodeTypeField(
    name="mode",
    type="str",
    required=True,
    input_type="select",
    default="single",
    choices=[
        {"label": "single", "value": "single"},
        {"label": "elements", "value": "elements"},
        {"label": "page", "value": "page"},
    ],
)
UNSTRUCTURED_IO_FIELDS = [FILE_PATH_LIST, UNSTRUCTURED_IO_MODE]

UNSTRUCTURED_FILE_IO_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.unstructured.UnstructuredFileIOLoader"
)
UNSTRUCTURED_FILE_IO_LOADER = NodeType(
    class_path=UNSTRUCTURED_FILE_IO_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured File IO Loader",
    description="Load a file from an IO stream into a document with Unstructured.io.",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)

UNSTRUCTURED_API_FILE_IO_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.unstructured.UnstructuredFileIOLoader"
)
UNSTRUCTURED_API_FILE_IO_LOADER = NodeType(
    class_path=UNSTRUCTURED_API_FILE_IO_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured API File Loader",
    description="Load files using `Unstructured` API.",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS
    + NodeTypeField.get_fields(
        UnstructuredFileIOLoader,
        include=[
            "url",
        ],
        api_key={"input_type": "secret"},
    ),
)

UNSTRUCTURED_API_FILE_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.unstructured.UnstructuredAPIFileLoader"
)
UNSTRUCTURED_API_FILE_LOADER = NodeType(
    class_path=UNSTRUCTURED_API_FILE_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured API File Loader",
    description="Load files using `Unstructured` API.",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS
    + NodeTypeField.get_fields(
        UnstructuredAPIFileLoader,
        include=[
            "url",
        ],
        api_key={"input_type": "secret"},
    ),
)

UNSTRUCTURED_WORD_DOCUMENT_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.word_document.UnstructuredWordDocumentLoader"
)
UNSTRUCTURED_WORD_DOCUMENT_LOADER = NodeType(
    class_path=UNSTRUCTURED_WORD_DOCUMENT_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured Word Document Loader",
    description="Load a Word document into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)
UNSTRUCTURED_ODT_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.odt.UnstructuredODTLoader"
)
UNSTRUCTURED_ODT_LOADER = NodeType(
    class_path=UNSTRUCTURED_ODT_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured ODT Loader",
    description="Load an ODT file into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)
UNSTRUCTURED_PDF_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.pdf.UnstructuredPDFLoader"
)
UNSTRUCTURED_PDF_LOADER = NodeType(
    class_path=UNSTRUCTURED_PDF_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured PDF Loader",
    description="Load a PDF file into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)

UNSTRUCTURED_HTML_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.UnstructuredHTMLLoader"
)
UNSTRUCTURED_HTML_LOADER = NodeType(
    class_path=UNSTRUCTURED_HTML_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured HTML Loader",
    description="Load an HTML file into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=NodeTypeField.get_fields(
        UnstructuredHTMLLoader.__init__, include=["file_path" "mode"]
    ),
)

UNSTRUCTURED_CSV_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.csv_loader.UnstructuredCSVLoader"
)
UNSTRUCTURED_CSV_LOADER = NodeType(
    class_path=UNSTRUCTURED_CSV_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured CSV Loader",
    description="Load a CSV file into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)

UNSTRUCTURED_MARKDOWN_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.UnstructuredMarkdownLoader"
)
UNSTRUCTURED_MARKDOWN_LOADER = NodeType(
    class_path=UNSTRUCTURED_MARKDOWN_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured Markdown Loader",
    description="Load a Markdown file into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)

UNSTRUCTURED_RST_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.rst.UnstructuredRSTLoader"
)
UNSTRUCTURED_RST_LOADER = NodeType(
    class_path=UNSTRUCTURED_RST_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured RST Loader",
    description="Load an RST file into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)
UNSTRUCTURED_EPUB_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.epub.UnstructuredEPubLoader"
)
UNSTRUCTURED_EPUB_LOADER = NodeType(
    class_path=UNSTRUCTURED_EPUB_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured EPub Loader",
    description="Load an EPub file into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)
UNSTRUCTURED_XML_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.xml.UnstructuredXMLLoader"
)
UNSTRUCTURED_XML_LOADER = NodeType(
    class_path=UNSTRUCTURED_XML_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured XML Loader",
    description="Load an XML file into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)
UNSTRUCTURED_IMAGE_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.image.UnstructuredImageLoader"
)
UNSTRUCTURED_IMAGE_LOADER = NodeType(
    class_path=UNSTRUCTURED_IMAGE_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured Image Loader",
    description="Load an image file into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)
UNSTRUCTURED_EMAIL_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.email.UnstructuredEmailLoader"
)
UNSTRUCTURED_EMAIL_LOADER = NodeType(
    class_path=UNSTRUCTURED_EMAIL_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured Email Loader",
    description="Load an email file into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)
UNSTRUCTURED_RTF_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.rtf.UnstructuredRTFLoader"
)
UNSTRUCTURED_RTF_LOADER = NodeType(
    class_path=UNSTRUCTURED_RTF_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured RTF Loader",
    description="Load an RTF file into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)
UNSTRUCTURED_ORG_MODE_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.org_mode.UnstructuredOrgModeLoader"
)
UNSTRUCTURED_ORG_MODE_LOADER = NodeType(
    class_path=UNSTRUCTURED_ORG_MODE_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured Org Mode Loader",
    description="Load an Org Mode file into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)
UNSTRUCTURED_POWERPOINT_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.powerpoint.UnstructuredPowerPointLoader"
)
UNSTRUCTURED_POWERPOINT_LOADER = NodeType(
    class_path=UNSTRUCTURED_POWERPOINT_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured PowerPoint Loader",
    description="Load a PowerPoint file into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)
UNSTRUCTURED_EXCEL_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.excel.UnstructuredExcelLoader"
)
UNSTRUCTURED_EXCEL_LOADER = NodeType(
    class_path=UNSTRUCTURED_EXCEL_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured Excel Loader",
    description="Load an Excel file into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)
UNSTRUCTURED_TSV_LOADER_CLASS_PATH = (
    "langchain_community.document_loaders.tsv.UnstructuredTSVLoader"
)
UNSTRUCTURED_TSV_LOADER = NodeType(
    class_path=UNSTRUCTURED_TSV_LOADER_CLASS_PATH,
    type="document_loader",
    name="Unstructured TSV Loader",
    description="Load a TSV file into a document with Unstructured.io",
    connectors=LOADER_CONNECTORS,
    fields=UNSTRUCTURED_IO_FIELDS,
)

UNSTRUCTURED_IO = [
    # UNSTRUCTURED_FILE_IO_LOADER,  # disabled because nothing else uses IO classes yet.
    # UNSTRUCTURED_API_FILE_IO_LOADER,
    UNSTRUCTURED_API_FILE_LOADER,
    UNSTRUCTURED_WORD_DOCUMENT_LOADER,
    UNSTRUCTURED_ODT_LOADER,
    UNSTRUCTURED_PDF_LOADER,
    UNSTRUCTURED_HTML_LOADER,
    UNSTRUCTURED_CSV_LOADER,
    UNSTRUCTURED_MARKDOWN_LOADER,
    UNSTRUCTURED_RST_LOADER,
    UNSTRUCTURED_EPUB_LOADER,
    UNSTRUCTURED_XML_LOADER,
    UNSTRUCTURED_IMAGE_LOADER,
    UNSTRUCTURED_EMAIL_LOADER,
    UNSTRUCTURED_RTF_LOADER,
    UNSTRUCTURED_ORG_MODE_LOADER,
    UNSTRUCTURED_POWERPOINT_LOADER,
    UNSTRUCTURED_EXCEL_LOADER,
    UNSTRUCTURED_TSV_LOADER,
]
