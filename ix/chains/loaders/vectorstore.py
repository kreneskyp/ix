import logging
from copy import deepcopy
from typing import Dict, Any, Type

from langchain.document_loaders.base import BaseLoader
from langchain.vectorstores import VectorStore

from ix.chains.fixture_src.vectorstores import get_vectorstore_retriever_fieldnames
from ix.chains.loaders.text_splitter import TextSplitterShim
from ix.utils.importlib import import_class


logger = logging.getLogger(__name__)


def initialize_vectorstore(class_path: str, config: Dict[str, Any]) -> VectorStore:
    """
    Initialize vectorstore

    Documents may come from either a TextSplitter or BaseLoader. Determine the type
    it is and initialize accordingly.
    """
    config = config.copy()

    # remove retriever fields from the config, if present
    retriever_fields = get_vectorstore_retriever_fieldnames(class_path)
    for field in retriever_fields:
        config.pop(field, None)

    # initialize vectorstore
    vectorstore_class: Type[VectorStore] = import_class(class_path)
    vectorstore = None

    # Ingest and load from documents if TextSplitters or BaseLoaders
    # is configured as a document source.
    document_source = config.pop("documents", None)
    if document_source:
        if isinstance(document_source, TextSplitterShim):
            document_loader = document_source.document_loader
            documents = document_source.text_splitter.split_documents(
                document_loader.load()
            )
        elif isinstance(document_source, BaseLoader):
            documents = document_source.load()

        else:
            raise ValueError(
                f"unsupported document_source type: {type(document_source)}"
            )

        if documents:
            vectorstore = vectorstore_class.from_documents(
                documents=documents, **config
            )

    # Initialize vectorstore without ingesting documents. The vectorstore will
    # only have access to documents that are already in the database.
    if not vectorstore:
        embedding_function = config.pop("embedding", None)
        if embedding_function:
            config["embedding_function"] = embedding_function
        vectorstore = vectorstore_class(**config)

    return vectorstore
