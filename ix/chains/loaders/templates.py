from typing import TypeVar, Generic, Dict, Any, Set, Type

from asgiref.sync import sync_to_async
from pydantic import BaseModel

from ix.chains.loaders.context import IxContext
from ix.chains.models import ChainNode
from ix.utils.config import get_config_variables
from ix.utils.pydantic import create_args_model

T = TypeVar("T")


class NodeTemplate(Generic[T]):
    """
    A template for a node in a chain. This is used to create a node from a graph whose
    nodes contain $variables.

    Templates containing $variables are used as placeholders to delay instantiation
    until request time. This allows for dynamic configuration of nodes from chain
    inputs.

    The most common example is a document loader. Document loaders are used to load
    documents into a vectorstore. Document loaders generally require a path or URL
    to the source document. Using a template, document loaders can be reused
    for different source documents.
    """

    def __init__(self, node: ChainNode, context: IxContext):
        self.node = node
        self.context = context

    def format(self, input: Dict[str, Any]) -> T:
        from ix.chains.loaders.core import load_node

        return load_node(self.node, self.context, variables=input)

    async def aformat(self, input: Dict[str, Any]) -> T:
        from ix.chains.loaders.core import load_node

        return await sync_to_async(load_node)(self.node, self.context, variables=input)

    def get_variables(self, node: ChainNode = None) -> Set[str]:
        """
        Helper recursive function to extract config variables.
        """
        node = node if node else self.node
        variables = get_config_variables(node.config if node.config else {})

        # Recursively traverse for all connected nodes
        connected_edges = node.incoming_edges.filter(relation="PROP").order_by(
            "target_key"
        )
        for edge in connected_edges.iterator():
            connected_node = ChainNode.objects.get(pk=edge.source_id)
            variables.update(self.get_variables(connected_node))

        return variables

    async def aget_variables(self, node: ChainNode = None) -> Set[str]:
        """
        Helper recursive function to extract config variables.
        """
        node = node if node else self.node
        variables = get_config_variables(node.config if node.config else {})

        # Recursively traverse for all connected nodes
        connected_edges = node.incoming_edges.filter(relation="PROP").order_by("key")
        async for edge in connected_edges.aiterator():
            connected_node = await ChainNode.objects.aget(pk=edge.source_id)
            variables.update(await self.get_variables(connected_node))

        return variables

    def get_args_schema(self) -> Type[BaseModel]:
        """
        Dynamically create a Pydantic model class with fields for each variable in the template.
        """
        variables = self.get_variables()
        return create_args_model(variables, name="NodeTemplateSchema")
