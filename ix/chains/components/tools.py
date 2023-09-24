from typing import Any, Union, Optional, Dict
from langchain.schema import BaseRetriever
from langchain.schema.runnable import RunnableConfig
from langchain.tools import BaseTool, Tool
from langchain.vectorstores import VectorStore

from ix.chains.loaders.templates import NodeTemplate


class IngestionTool(BaseTool):
    """
    Tool that loads data into a vectorstore using a templates retriever.
    """

    # TODO: needs to lazy load func and coroutine
    # TODO: needs to generate function spec from the classes reference to func
    # TODO: Need to inform loader to lazy load the retriever: Templated type.
    # TODO: maybe a good reason to automate pulling in connectors.

    retriever_template: NodeTemplate[BaseRetriever]
    vectorstore: VectorStore

    def invoke(self):
        # create retriever from template
        retriever = self.retriever.from_template(
            input=input,
        )

        # create tool from inputs
        return Tool(
            name=self.name,
            description=self.description,
            func=retriever.get_relevant_documents,
        )

    async def ainvoke(
        self,
        input: Union[str, Dict],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Any:
        # create retriever from template
        retriever = self.retriever.format(
            input=input,
        )

        # create tool from inputs
        return Tool(
            name=self.name,
            description=self.description,
            coroutine=retriever.aget_relevant_documents,
        )
