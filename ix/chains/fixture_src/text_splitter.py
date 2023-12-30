from langchain.text_splitter import (
    TextSplitter,
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)

from ix.api.components.types import NodeTypeField
from ix.chains.fixture_src.document_loaders import DOCUMENTS_OUTPUT, DOCUMENTS_INPUT
from ix.chains.fixture_src.parsers import LANGUAGE

DOCUMENT_TRANSFORMER_CONNECTORS = [
    DOCUMENTS_INPUT,
    DOCUMENTS_OUTPUT,
]


CHARACTER_SPLITTER_CLASS_PATH = "langchain.text_splitter.CharacterTextSplitter"
CHARACTER_SPLITTER = {
    "class_path": CHARACTER_SPLITTER_CLASS_PATH,
    "type": "text_splitter",
    "name": "CharacterTextSplitter",
    "description": CharacterTextSplitter.__doc__,
    "connectors": DOCUMENT_TRANSFORMER_CONNECTORS,
    "fields": NodeTypeField.get_fields(
        TextSplitter.__init__,
        include=[
            "separator",
            "chunk_size",
            "chunk_overlap",
            "keep_separator",
            "add_start_index",
        ],
    ),
}


RECURSIVE_CHARACTER_SPLITTER_CLASS_PATH = (
    "langchain.text_splitter.RecursiveCharacterTextSplitter.from_language"
)

RECURSIVE_CHARACTER_SPLITTER = {
    "class_path": RECURSIVE_CHARACTER_SPLITTER_CLASS_PATH,
    "type": "text_splitter",
    "name": "RecursiveCharacterTextSplitter",
    "description": RecursiveCharacterTextSplitter.__doc__,
    "connectors": DOCUMENT_TRANSFORMER_CONNECTORS,
    "fields": [LANGUAGE]
    + NodeTypeField.get_fields(
        TextSplitter.__init__,
        include=[
            "chunk_size",
            "chunk_overlap",
            "keep_separator",
            "add_start_index",
        ],
    ),
}

TEXT_SPLITTERS = [RECURSIVE_CHARACTER_SPLITTER, CHARACTER_SPLITTER]

__all__ = ["TEXT_SPLITTERS", "RECURSIVE_CHARACTER_SPLITTER_CLASS_PATH"]
