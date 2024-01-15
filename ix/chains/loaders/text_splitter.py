from copy import deepcopy
from typing import Dict, Any

from langchain_community.document_loaders.base import BaseLoader
from langchain.text_splitter import TextSplitter
from pydantic import BaseModel

from ix.utils.importlib import import_class


class TextSplitterShim(BaseModel):
    document_loader: BaseLoader
    text_splitter: TextSplitter

    class Config:
        arbitrary_types_allowed = True


def initialize_text_splitter(
    class_path: str, config: Dict[str, Any]
) -> TextSplitterShim:
    """Initialize text splitter:

    Text splitters are used to split documents into chunks. The documents generally come from
    a BaseLoader.load() call. The TextSplitter class doesn't store the BaseLoader as a property.
    The two classes are expected to be instantiated separately and then documents split using
    the TextSplitter.split_documents() method.

    This initializer uses TextSplitterShim to capture the relationship between the two classes.
    Downstream consumers can use the TextSplitterShim to access the BaseLoader and TextSplitter
    to split the documents.
    """
    config_copy = deepcopy(config)
    document_source = config_copy.pop("document_loader")

    default_initializer = import_class(class_path)
    text_splitter = default_initializer(**config_copy)
    return TextSplitterShim(
        document_loader=document_source, text_splitter=text_splitter
    )
