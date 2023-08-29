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
            "config": {"streaming": True},
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

DAD_JOKES_CHAIN_V1 = "b7d8f662-12f6-4525-b07b-c9ea7c10003c"
DAD_JOKES_AGENT_V1 = "b7d8f662-12f6-4525-b07b-c9ea7c10003a"


class Command(BaseCommand):
    help = "Creates planning chain v1"

    def handle(self, *args, **options):
        chain, _ = Chain.objects.get_or_create(
            pk=DAD_JOKES_CHAIN_V1,
            defaults=dict(
                name="Dad jokes chain",
                description="Chain used to generate dad jokes",
            ),
        )
        chain.clear_chain()

        # Create root node
        ChainNode.objects.create(chain=chain, root=True, **DAD_JOKESTER)

        Agent.objects.get_or_create(
            id=DAD_JOKES_AGENT_V1,
            defaults=dict(
                name="Dad Jokester",
                alias="dad",
                purpose="to generate dad jokes",
                chain=chain,
                config={},
            ),
        )
