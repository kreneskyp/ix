import logging
from typing import Any

from langchain.document_loaders.base import BaseLoader
from langchain.schema import BaseRetriever
from langchain.schema.vectorstore import VectorStore
from langchain.text_splitter import TextSplitter
from langchain.tools import BaseTool

from ix.chains.loaders.templates import NodeTemplate
from ix.chains.loaders.text_splitter import TextSplitterShim
from ix.utils.pydantic import create_args_model


logger = logging.getLogger(__name__)


class IngestionTool(BaseTool):
    """
    Tool that loads data into a vectorstore using a templates retriever.
    """

    loader_template: NodeTemplate[BaseRetriever | TextSplitter]
    vectorstore: NodeTemplate[VectorStore]

    def __init__(self, *args, **kwargs):
        name = kwargs.pop("name", "ingest")
        description = kwargs.pop("description", "Ingest data into a vectorstore")

        super().__init__(name=name, description=description, *args, **kwargs)

        # set args_schema containing template_variables from all templates
        template_variables = self.loader_template.get_variables()
        template_variables.update(self.vectorstore.get_variables())
        self.args_schema = create_args_model(
            template_variables, name="NodeTemplateSchema"
        )

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
        logger.debug(f"IngestionTool.arun: {kwargs}")

        # create retriever from template
        loader = await self.loader_template.aformat(
            input=kwargs,
        )

        vectorstore = await self.vectorstore.aformat(
            input=kwargs,
        )

        if isinstance(loader, TextSplitterShim):
            document_loader = loader.document_loader
            documents = loader.text_splitter.split_documents(document_loader.load())
        elif isinstance(loader, BaseLoader):
            documents = loader.load()

        document_ids = await vectorstore.aadd_documents(documents)
        return {"document_ids": document_ids}
