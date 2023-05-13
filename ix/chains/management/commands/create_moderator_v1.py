from django.core.management.base import BaseCommand
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


CHAIN_ID = "b7d8f662-12f6-4525-b07b-c9ea7ca7f200"


class Command(BaseCommand):
    help = "Creates planning chain v1"

    def handle(self, *args, **options):
        Chain.objects.filter(id=CHAIN_ID).delete()

        # Create root node
        root = ChainNode.objects.create(**CHAT_MODERATOR)

        Chain.objects.create(
            pk=CHAIN_ID,
            name="Chat Moderation Chain",
            description="Chain used moderate chats. The moderator analyzes user input "
            "and delegates it to the appropriate agent.",
            root=root,
        )
