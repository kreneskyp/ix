from typing import Any

from langchain.document_loaders.base import BaseLoader
from langchain.schema import BaseRetriever
from langchain.text_splitter import TextSplitter
from langchain.tools import BaseTool
from langchain.vectorstores import VectorStore

from ix.chains.loaders.templates import NodeTemplate
from ix.chains.loaders.text_splitter import TextSplitterShim


class IngestionTool(BaseTool):
    """
    Tool that loads data into a vectorstore using a templates retriever.
    """

    loader_template: NodeTemplate[BaseRetriever | TextSplitter]
    vectorstore: VectorStore

    def __init__(self, *args, **kwargs):
        name = kwargs.pop("name", "ingest")
        description = kwargs.pop("description", "Ingest data into a vectorstore")

        super().__init__(name=name, description=description, *args, **kwargs)

        # set args_schema from template variables
        self.args_schema = self.loader_template.get_args_schema()

    def _run(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        # create retriever from template
        loader = self.loader_template.format(
            input=kwargs.get("tool_input", {}),
        )

        if isinstance(loader, TextSplitterShim):
            document_loader = loader.document_loader
            documents = loader.text_splitter.split_documents(document_loader.load())
        elif isinstance(loader, BaseLoader):
            documents = loader.load()

        document_ids = self.vectorstore.add_documents(documents)
        return {"document_ids": document_ids}

    async def _arun(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        # create retriever from template
        loader = await self.loader_template.aformat(
            input=kwargs,
        )

        if isinstance(loader, TextSplitterShim):
            document_loader = loader.document_loader
            documents = loader.text_splitter.split_documents(document_loader.load())
        elif isinstance(loader, BaseLoader):
            documents = loader.load()

        document_ids = await self.vectorstore.aadd_documents(documents)
        return {"document_ids": document_ids}
