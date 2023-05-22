from django.core.management.base import BaseCommand

from ix.agents.models import Agent
from ix.chains.models import ChainNode, Chain


CHAT_MODERATOR = {
    "class_path": "ix.chains.moderator.ChatModerator",
    "node_type": "map",
    "config": {
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
            "config": {"temperature": 0},
        },
    },
}


MODERATOR_CHAIN_V1 = "b7d8f662-12f6-4525-b07b-c9ea7c10001c"
MODERATOR_AGENT_V1 = "b7d8f662-12f6-4525-b07b-c9ea7c10001a"


class Command(BaseCommand):
    help = "Creates planning chain v1"

    def handle(self, *args, **options):
        Chain.objects.filter(id=MODERATOR_CHAIN_V1).delete()

        # Create root node
        root = ChainNode.objects.create(**CHAT_MODERATOR)

        chain = Chain.objects.create(
            pk=MODERATOR_CHAIN_V1,
            name="Chat Moderation Chain",
            description="Chain used moderate chats. The moderator analyzes user input "
            "and delegates it to the appropriate agent.",
            root=root,
        )

        Agent.objects.create(
            id=MODERATOR_AGENT_V1,
            name="Ix",
            alias="ix",
            purpose="Ix is the moderator agent. It analyzes user input and delegates to other agents.",
            chain=chain,
            config={},
        )
