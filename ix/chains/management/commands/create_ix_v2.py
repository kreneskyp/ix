from django.core.management.base import BaseCommand

from ix.agents.models import Agent
from ix.chains.models import ChainNode, Chain
from ix.chains.moderator import LLM_CHOOSE_AGENT_CONFIG


CHAT_MODERATOR = {
    "class_path": "ix.chains.moderator.ChatModerator",
    "config": {
        "selection_chain": LLM_CHOOSE_AGENT_CONFIG,
        "memory": [
            {
                "class_path": "langchain.memory.ConversationBufferMemory",
                "config": {
                    "memory_key": "chat_history",
                    "input_key": "user_input",
                    "output_key": "text",
                    "chat_memory": {
                        "class_path": "langchain.memory.RedisChatMessageHistory",
                        "config": {
                            "url": "redis://redis:6379/0",
                            "session_scope": "chat",
                        },
                    },
                },
            },
        ],
    },
}

IX_CHAIN_V2 = "b7d8f662-12f6-4525-b07b-c9ea7c10001c"
IX_AGENT_V2 = "b7d8f662-12f6-4525-b07b-c9ea7c10001a"


class Command(BaseCommand):
    help = "Creates planning chain v1"

    def handle(self, *args, **options):
        chain, _ = Chain.objects.get_or_create(
            pk=IX_CHAIN_V2,
            defaults=dict(
                name="IX Chat Moderation Chain",
                description="Core IX agent used moderate chats. The moderator analyzes user input "
                "and delegates it to the appropriate agent.",
            ),
        )

        # create chain nodes
        chain.clear_chain()
        ChainNode.objects.create_from_config(
            chain=chain, root=True, config=CHAT_MODERATOR
        )

        Agent.objects.get_or_create(
            id=IX_AGENT_V2,
            defaults=dict(
                name="Ix",
                alias="ix",
                purpose="Ix is the moderator agent. It analyzes user input and delegates to other agents.",
                chain=chain,
                config={},
            ),
        )
