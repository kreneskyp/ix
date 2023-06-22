from django.core.management.base import BaseCommand

from ix.agents.models import Agent
from ix.chains.models import ChainNode, Chain, NodeType
from ix.chains.moderator import LLM_CHOOSE_AGENT_CONFIG

SELECTION_CHAIN_TARGET = {
    "key": "selection_chain",
    "type": "target",
    "source_type": "chain",
}


CHAT_MODERATOR_TYPE = {
    "class_path": "ix.chains.moderator.ChatModerator",
    "name": "IX Chat Moderator",
    "description": "Chat moderator analyzes user input and delegates it to the appropriate agent.",
    "type": "chain",
    "display_type": "node",
    "connectors": [SELECTION_CHAIN_TARGET],
}


CHAT_MODERATOR = {
    "class_path": "ix.chains.moderator.ChatModerator",
    "config": {"selection_chain": LLM_CHOOSE_AGENT_CONFIG},
}

MODERATOR_TYPE_V1 = "b7d8f662-12f6-4525-b07b-c9ea7c10001d"
MODERATOR_CHAIN_V1 = "b7d8f662-12f6-4525-b07b-c9ea7c10001c"
MODERATOR_AGENT_V1 = "b7d8f662-12f6-4525-b07b-c9ea7c10001a"


class Command(BaseCommand):
    help = "Creates planning chain v1"

    def handle(self, *args, **options):
        node_type, _ = NodeType.objects.get_or_create(
            pk=MODERATOR_TYPE_V1, defaults=CHAT_MODERATOR_TYPE
        )
        node_type.connectors = CHAT_MODERATOR_TYPE["connectors"]
        node_type.save()

        chain, _ = Chain.objects.get_or_create(
            pk=MODERATOR_CHAIN_V1,
            defaults=dict(
                name="Chat Moderation Chain",
                description="Chain used moderate chats. The moderator analyzes user input "
                "and delegates it to the appropriate agent.",
            ),
        )

        # create chain nodes
        chain.clear_chain()
        ChainNode.objects.create_from_config(
            chain=chain, root=True, config=CHAT_MODERATOR
        )

        Agent.objects.get_or_create(
            id=MODERATOR_AGENT_V1,
            defaults=dict(
                name="Ix",
                alias="ix",
                purpose="Ix is the moderator agent. It analyzes user input and delegates to other agents.",
                chain=chain,
                config={},
            ),
        )
