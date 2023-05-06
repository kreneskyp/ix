import logging
import uuid
from typing import Any, Dict, Optional

from django.db import models
from langchain.chains.base import Chain

from ix.utils.importlib import import_class

logger = logging.getLogger(__name__)


class ChainNode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_path = models.CharField(max_length=255)
    config = models.JSONField(null=True)
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)

    node_type = models.CharField(
        max_length=10,
        default="node",
        choices=(("node", "node"), ("list", "list"), ("map", "map")),
    )

    # denormalized reference to root of graph.
    # Used for quickly selecting all nodes for a chain
    root = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="descendants",
        null=True,
        blank=True,
    )

    # reference to parent node that contains this node.
    # used to describe sequences and maps.
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="children", null=True, blank=True
    )

    def get_root(self) -> "ChainNode":
        """return the root of the chain"""
        return self.root if self.root else self

    def add_node(self, key: str = "tools", **kwargs) -> "ChainNode":
        """Add a node to the root"""
        logger.debug(f"adding node to {self.class_path} kwargs={kwargs}")
        root = self.get_root()
        node = ChainNode.objects.create(root=root, **kwargs)
        ChainEdge.objects.create(
            root=root,
            source=root,
            target=node,
            key=key,
        )
        return node

    def add_child(self, key: Optional[str] = None, **kwargs) -> "ChainNode":
        """Add a node as a child"""
        logger.debug(f"adding child to {self.class_path} kwargs={kwargs}")
        root = self.get_root()
        parent = self

        # auto-set ordering key for edges within lists
        latest_node = None
        if not key and parent.node_type == "list":
            try:
                latest_node = self.children.all().latest("incoming_edges__key")
                edge = latest_node.incoming_edges.get()
                last_key = int(edge.key)
                logger.debug(f"found last child key={last_key}")
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
        node = ChainNode.objects.create(root=root, parent=parent, **kwargs)
        ChainEdge.objects.create(
            root=root,
            source=source_node,
            target=node,
            key=key,
        )
        return node

    def load_config(self) -> Dict[str, Any]:
        logger.debug("Loading config for: ", self.name, self.class_path)
        config = self.config.copy() if self.config else {}

        if self.node_type == "list":
            child_chains = []
            for i, child in enumerate(
                self.children.all().order_by("incoming_edges__key")
            ):
                child_chains.append(child.load_config())
            config["chains"] = child_chains
        elif self.node_type == "map":
            # The chain class expects a list and will build its own map
            config["tools"] = [
                edge.target.load_config()
                for edge in self.outgoing_edges.select_related("target")
            ]

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(
        ChainNode, on_delete=models.CASCADE, related_name="outgoing_edges"
    )
    target = models.ForeignKey(
        ChainNode, on_delete=models.CASCADE, related_name="incoming_edges"
    )
    key = models.CharField(max_length=255, null=True)
    root = models.ForeignKey(ChainNode, on_delete=models.CASCADE, related_name="edges")
    input_map = models.JSONField(null=True)


class Chain(models.Model):
    """
    A named chain that can be run by an Agent.

    Each chain has a root ChainNode representing the start of the chain.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    root = models.ForeignKey(ChainNode, on_delete=models.CASCADE, related_name="chains")

    def load_chain(self, callback_manager) -> Chain:
        # from ix.agents.callback_manager import IxCallbackManager

        # callback_manager = IxCallbackManager(None)
        return self.root.load_chain(callback_manager)

    def run(self):
        """Run the chain"""
        self.root.run()
