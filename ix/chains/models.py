import logging
import uuid
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

    @cached_property
    def connectors_as_dict(self):
        return {c["key"]: c for c in self.connectors or []}


def default_position():
    return {"x": 0, "y": 0}


class ChainNode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_path = models.CharField(max_length=255)
    node_type = models.ForeignKey(NodeType, on_delete=models.CASCADE, null=True)
    config = models.JSONField(null=True)
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

    def add_node(self, key: str = "tools", **kwargs) -> "ChainNode":
        """Add a node to the root"""
        logger.debug(f"adding node to {self.class_path} kwargs={kwargs}")
        node = ChainNode.objects.create(root=self.root, **kwargs)
        ChainEdge.objects.create(
            chain_id=self.chain_id,
            source=self,
            target=node,
            key=key,
        )
        return node

    def add_child(self, key: Optional[str] = None, **kwargs) -> "ChainNode":
        """Add a node as a child"""
        parent = self

        # auto-set ordering key for edges within lists
        latest_node = None
        if not key and parent.node_type == "list":
            try:
                latest_node = self.children.all().latest("incoming_edges__key")
                edge = latest_node.incoming_edges.get()
                last_key = int(edge.key)
            except ChainNode.DoesNotExist:
                last_key = 0
            key = f"{last_key+1:0>3}"

        # default key for map types is chains
        elif not key and parent.node_type == "map":
            key = "chains"

        # Chain the edges from parent -> nodes -> new node
        # if no node then start with parent
        source_node = latest_node or parent

        logger.debug(f"adding child to {self.class_path} key={key} kwargs={kwargs}")
        node = ChainNode.objects.create(chain_id=self.chain_id, parent=parent, **kwargs)
        ChainEdge.objects.create(
            chain_id=self.chain_id,
            source=source_node,
            target=node,
            key=key,
        )
        return node

    def load_config(self) -> Dict[str, Any]:
        logger.debug(
            f"Loading config for: name={self.name} class_path={self.class_path}"
        )
        config = self.config.copy() if self.config else {}

        if self.node_type == "list":
            child_chains = []
            for i, child in enumerate(
                self.children.all().order_by("incoming_edges__key")
            ):
                child_chains.append(child.load_config())
            config["chains"] = child_chains
        elif self.node_type == "map":
            for edge in self.outgoing_edges.select_related("target"):
                try:
                    target = config[edge.key]
                except KeyError:
                    target = []
                    config[edge.key] = target
                target.append(edge.target.load_config())

        return {
            "name": self.name,
            "description": self.description,
            "class_path": self.class_path,
            "config": config,
        }

    def load_chain(self, callback_manager):
        config = self.load_config()
        chain_class = import_class(self.class_path)
        return chain_class.from_config(
            config=config["config"], callback_manager=callback_manager
        )


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

    @property
    def root(self) -> ChainNode:
        try:
            return self.nodes.get(root=True)
        except ChainNode.DoesNotExist:
            raise ValueError(f"Chain chain_id={self.id} does not have a root node")

    def load_chain(self, callback_manager) -> LangChain:
        return self.root.load_chain(callback_manager)

    def run(self):
        """Run the chain"""
        self.root.run()

    def clear_chain(self):
        """removes the chain nodes associated with this chain"""
        # clear old chain
        ChainNode.objects.filter(chain_id=self.id).delete()
