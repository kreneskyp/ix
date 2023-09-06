from copy import deepcopy
from typing import List

from asgiref.sync import sync_to_async
from langchain.schema import BaseRetriever
from langchain.vectorstores import VectorStore

from ix.chains.fixture_src.vectorstores import get_vectorstore_retriever_fieldnames
from ix.chains.loaders.context import IxContext
from ix.chains.loaders.core import load_node
from ix.chains.models import ChainNode
from ix.utils.importlib import import_class


async def async_aget_relevant_documents(self, *args, **kwargs):
    """Async wrapper for BaseRetriever._get_relevant_documents"""
    return await sync_to_async(self._get_relevant_documents)(*args, **kwargs)


# HAX: monkeypatch asyncio support into BaseRetriever. This is a gigantic hack, but
#      it's the easiest way to get support for all retrievers without having to
#      modify langchain or implement lots of custom wrappers.
setattr(BaseRetriever, "_aget_relevant_documents", async_aget_relevant_documents)


def load_retriever_property(
    node_group: List[ChainNode], context: IxContext
) -> BaseRetriever:
    """Property loader for retriever.

    Retrievers may be BaseRetriever or VectorStore. The latter must be converted to
    a retriever by calling `vectorstore.as_retriever`. This allows for VectorStore
    to determine the exact Retriever subclass (e.g. redis has a custom retriever).
    """

    assert len(node_group) == 1
    node = node_group[0]
    component_class = import_class(node.class_path)

    if isinstance(component_class, type) and issubclass(component_class, VectorStore):
        # unpack retriever fields from vectorstore config
        config = deepcopy(node.config)
        retriever_fields = get_vectorstore_retriever_fieldnames(node.class_path)
        retriever_config = {}
        for field in retriever_fields:
            if field in config:
                retriever_config[field] = config[field]

        # load vectorstore and then convert to retriever
        component = load_node(node, context)
        return component.as_retriever(**retriever_config)

    else:
        # return as a regular component
        return load_node(node, context)
