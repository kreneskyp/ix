from django.core.management.base import BaseCommand

from ix.agents.models import Agent
from ix.chains.models import ChainNode, Chain


FAKE_DAD_JOKES_PROMPT = (
    """You are a dad who enjoys making dad jokes. The pun-ier the better."""
    """Incorporate any user_input into the joke."""
)

DAD_JOKESTER = {
    "class_path": "ix.chains.llm_chain.LLMReply",
    "config": {
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
        },
        "messages": [
            {"role": "system", "template": FAKE_DAD_JOKES_PROMPT},
            {
                "role": "user",
                "template": "{user_input}",
                "input_variables": ["user_input"],
            },
        ],
    },
}

CHAIN_ID = "b7d8f662-12f6-4525-b07b-c9ea7ca79001"


class Command(BaseCommand):
    help = "Creates planning chain v1"

    def handle(self, *args, **options):
        Chain.objects.filter(id=CHAIN_ID).delete()

        # Create root node
        root = ChainNode.objects.create(**DAD_JOKESTER)

        chain = Chain.objects.create(
            pk=CHAIN_ID,
            name="Dad jokes chain",
            description="Chain used to generate dad jokes",
            root=root,
        )

        Agent.objects.create(
            name="Dad Jokester",
            alias="dad",
            purpose="to generate dad jokes",
            chain=chain,
            config={},
        )
