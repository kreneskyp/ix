from copy import deepcopy
from typing import Dict, Any, Type

from langchain.vectorstores import VectorStore

from ix.chains.fixture_src.vectorstores import get_vectorstore_retriever_fieldnames
from ix.chains.loaders.text_splitter import TextSplitterShim
from ix.utils.importlib import import_class


def initialize_vectorstore(class_path: str, config: Dict[str, Any]) -> VectorStore:
    """
    Initialize vectorstore

    Documents may come from either a TextSplitter or BaseLoader. Determine the type
    it is and initialize accordingly.
    """
    config = deepcopy(config)

    # remove retriever fields from the config, if present
    retriever_fields = get_vectorstore_retriever_fieldnames(class_path)
    for field in retriever_fields:
        config.pop(field, None)

    # auto load documents from TextSplitters and BaseLoaders
    document_source = config.pop("documents", None)
    if document_source:
        if isinstance(document_source, TextSplitterShim):
            document_loader = document_source.document_loader
            documents = document_source.text_splitter.split_documents(
                document_loader.load()
            )
        else:
            raise ValueError(
                f"unsupported document_source type: {type(document_source)}"
            )
    else:
        # Initialize without loading documents. This is useful for vectorstores that
        # are initialized separately from the chain.
        #
        # TODO: this won't work for VectorStores that expect at least one entry.
        #       e.g. Redis reads the dimensions from the first embedding rather
        #       than from the embeddings component. Revisit this in phase 2 to
        #       support splitting ingestion and querying.
        documents = []

    # initialize vectorstore
    vectorstore_class: Type[VectorStore] = import_class(class_path)
    return vectorstore_class.from_documents(documents=documents, **config)
