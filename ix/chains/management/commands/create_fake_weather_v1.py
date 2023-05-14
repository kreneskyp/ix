from django.core.management.base import BaseCommand

from ix.agents.models import Agent
from ix.chains.models import ChainNode, Chain


FAKE_WEATHERMAN_PROMPT = (
    """You are a fake weatherman, respond with fake weather predictions."""
    """If the user references a location, include it in your response."""
)

FAKE_WEATHERMAN = {
    "class_path": "ix.chains.llm_chain.LLMReply",
    "config": {
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
        },
        "messages": [
            {"role": "system", "template": FAKE_WEATHERMAN_PROMPT},
            {
                "role": "user",
                "template": "{user_input}",
                "input_variables": ["user_input"],
            },
        ],
    },
}

CHAIN_ID = "b7d8f662-12f6-4525-b07b-c9ea7ca79000"


class Command(BaseCommand):
    help = "Creates planning chain v1"

    def handle(self, *args, **options):
        Chain.objects.filter(id=CHAIN_ID).delete()

        # Create root node
        root = ChainNode.objects.create(**FAKE_WEATHERMAN)

        chain = Chain.objects.create(
            pk=CHAIN_ID,
            name="Fake weatherman chain",
            description="Chain used to generate fake weather predictions",
            root=root,
        )

        Agent.objects.create(
            name="Weatherman",
            alias="weather",
            purpose="to report the weather",
            chain=chain,
            config={},
        )
