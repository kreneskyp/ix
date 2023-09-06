import logging
import uuid
from asgiref.sync import sync_to_async
from functools import cached_property
from typing import Any, Dict

from django.db import models
from langchain.chains.base import Chain as LangChain

from ix.pg_vector.tests.models import PGVectorMixin
from ix.pg_vector.utils import get_embedding


logger = logging.getLogger(__name__)


class NodeTypeQuery(PGVectorMixin, models.QuerySet):
    """Mixing PGVectorMixin into the default QuerySet."""

    pass


class NodeTypeManager(models.Manager.from_queryset(NodeTypeQuery)):
    def create_with_embedding(self, name, description, class_path):
        """
        Creates a new NodeType object with a vector embedding generated
        from the given text using OpenAI's API.
        """
        text = f"{name} {description} {class_path}"
        embedding = get_embedding(text)
        return self.create(
            name=name,
            description=description,
            class_path=class_path,
            embedding=embedding,
        )


class NodeType(models.Model):
    TYPES = [
        ("agent", "agent"),
        ("chain", "chain"),
        ("chain_list", "chain_list"),
        ("document_loader", "document_loader"),
        ("embeddings", "embeddings"),
        ("index", "index"),
        ("llm", "llm"),
        ("memory", "memory"),
        ("memory_backend", "memory_backend"),
        ("prompt", "prompt"),
        ("retriever", "retriever"),
        ("tool", "tool"),
        ("toolkit", "toolkit"),
        ("text_splitter", "text_splitter"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    class_path = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    display_type = models.CharField(
        max_length=10,
        default="node",
        choices=(("node", "node"), ("list", "list"), ("map", "map")),
    )
    connectors = models.JSONField(null=True)
    fields = models.JSONField(null=True)

    # child_field is the name of the field that contains child nodes
    # used for parsing config objects
    child_field = models.CharField(max_length=32, null=True)

    # JSONSchema for the config object
    config_schema = models.JSONField(default=dict)

    @cached_property
    def connectors_as_dict(self):
        return {c["key"]: c for c in self.connectors or []}

    def __str__(self):
        return f"{self.class_path}"


def default_position():
    return {"x": 0, "y": 0}


class ChainNodeManager(models.Manager):
    def create_from_config(
        self, chain, config: Dict[str, Any], root=False, parent=None
    ) -> "ChainNode":
        """
        Create an instance from a config dict.

        This method will identify the NodeType from the class_path. The NodeType
        definition is used to recursively identify and parse nested property nodes
        and child nodes.
        """

        # get the node type
        class_path = config["class_path"]
        logger.debug(f"creating node from config class_path={class_path}")

        try:
            node_type = NodeType.objects.get(class_path=class_path)
        except NodeType.DoesNotExist:
            logger.error(f"NodeType with class_path={class_path} does not exist")
            raise

        # pop off nested and child nodes before creating node
        node_config = config.get("config", {}).copy()
        property_configs = {}
        child_configs = []
        for connector in node_type.connectors or []:
            if connector["type"] == "target" and connector["key"] in node_config:
                logger.debug(f"adding property key={connector['key']}")
                property_configs[connector["key"]] = node_config.pop(connector["key"])

        if node_type.child_field is not None:
            child_configs = property_configs.pop(node_type.child_field, [])

        # create this node if visible
        is_hidden = config.pop("hidden", False)
        if not is_hidden:
            node = self.create(
                chain=chain,
                node_type=node_type,
                root=root,
                position={"x": 0, "y": 0},
                **config,
            )

            # create nested property nodes and edges to them
            for key, property_config_group in property_configs.items():
                logger.debug(f"creating property node for key={key}")
                if not isinstance(property_config_group, list):
                    property_config_group = [property_config_group]

                for property_config in property_config_group:
                    nested_node = self.create_from_config(
                        chain=chain, config=property_config
                    )
                    ChainEdge.objects.create(
                        chain_id=node.chain_id,
                        source=nested_node,
                        target=node,
                        relation="PROP",
                        key=key,
                    )
        elif property_configs:
            logger.error(
                f"class_path={class_path} has properties but is not hidden, properties={property_configs}"
            )
            raise ValueError("hidden nodes cannot have properties")

        # Handle children: Nodes with children may be hidden or visible
        # Hidden nodes are used with SequentialNodes to simplify the graph
        # UX. The children are visible and linked together. SequentialNodes
        # when visible display the children as a property node. This allows
        # both a simplified graph where nodes are linked together, and also
        # supports adding common properties to the SequentialNode when needed.
        if node_type.child_field is not None:
            logger.debug(
                f"node_id={node.id} loading children from field={node_type.child_field}"
            )
            latest_child = None
            for i, child in enumerate(child_configs):
                logger.debug(
                    f"node_id={node.id} creating child i={i} child={class_path}"
                )

                # create child
                source_node = latest_child
                latest_child = self.create_from_config(
                    chain=chain, config=child, root=root and i == 0 and is_hidden
                )

                # Link adjacent siblings
                if source_node:
                    ChainEdge.objects.create(
                        chain=chain,
                        source=source_node,
                        target=latest_child,
                        relation="LINK",
                    )

                # Add first node as property when visible
                if i == 0 and not is_hidden:
                    ChainEdge.objects.create(
                        chain=chain,
                        source=latest_child,
                        target=node,
                        relation="PROP",
                        key=node_type.child_field,
                    )

        logger.debug(f"created node_id={node.id} class_path={node.class_path}")
        return node


class ChainNode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_path = models.CharField(max_length=255)
    node_type = models.ForeignKey(NodeType, on_delete=models.CASCADE, null=True)
    config = models.JSONField(null=True, default=dict)
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)

    # node is root of graph
    root = models.BooleanField(default=False)

    # graph position
    position = models.JSONField(default=default_position)

    # parent chain
    chain = models.ForeignKey(
        "Chain",
        on_delete=models.CASCADE,
        related_name="nodes",
        null=True,
        blank=True,
    )

    objects = ChainNodeManager()

    def __str__(self):
        return f"{str(self.id)[:8]} ({self.class_path})"

    def load(self, context, root=True):
        """
        Load this node, traversing the graph and loading all child nodes,
        properties, and downstream nodes.
        """
        from ix.chains.loaders.core import load_node

        return load_node(self, context, root=root)


class ChainEdge(models.Model):
    RELATION_CHOICES = (("PROP", "prop"), ("LINK", "link"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(
        ChainNode, on_delete=models.CASCADE, related_name="outgoing_edges"
    )
    target = models.ForeignKey(
        ChainNode, on_delete=models.CASCADE, related_name="incoming_edges"
    )
    key = models.CharField(max_length=255, null=True)
    chain = models.ForeignKey(
        "Chain", on_delete=models.CASCADE, related_name="edges", null=True
    )
    input_map = models.JSONField(null=True)
    relation = models.CharField(
        max_length=4, null=True, choices=RELATION_CHOICES, default="LINK"
    )


class Chain(models.Model):
    """
    A named chain that can be run by an Agent.

    Each chain has a root ChainNode representing the start of the chain.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Indicate that this chain is an agent. This is used to record the config choice.
    # The endpoints are responsible for ensuring that the agent does or does not exist.
    is_agent = models.BooleanField(default=True)

    @property
    def root(self) -> ChainNode:
        try:
            return self.nodes.get(root=True)
        except ChainNode.DoesNotExist:
            raise ValueError(f"Chain chain_id={self.id} does not have a root node")

    def __str__(self):
        return f"{self.name} ({self.id})"

    def load_chain(self, context) -> LangChain:
        return self.root.load(context)

    async def aload_chain(self, context) -> LangChain:
        root = await ChainNode.objects.aget(chain_id=self.id, root=True)
        return await sync_to_async(root.load)(context)

    def clear_chain(self):
        """removes the chain nodes associated with this chain"""
        # clear old chain
        ChainNode.objects.filter(chain_id=self.id).delete()
