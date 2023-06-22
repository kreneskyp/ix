from django.core.management.base import BaseCommand

from ix.agents.models import Agent
from ix.chains.models import ChainNode, Chain

# Prompt includes variables for both ArtifactMemory and ConversationSummaryBufferMemory
PIRATE_PROMPT = """
You are a pirate. Talk like a pirate in all responses.

{related_artifacts}

CHAT_SUMMARY:
{chat_summary}
"""

# Pirate chain config includes two memory classes that are combined automatically
# by the Ix loader using `langchain.memory.CombinedMemory`
PIRATE = {
    "class_path": "ix.chains.llm_chain.LLMReply",
    "config": {
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
        },
        "memory": [
            {"class_path": "ix.memory.artifacts.ArtifactMemory"},
            {
                "class_path": "langchain.memory.summary_buffer.ConversationSummaryBufferMemory",
                "config": {
                    "input_key": "user_input",
                    "memory_key": "chat_summary",
                    "max_token_limit": 1500,
                    "llm": {
                        "class_path": "langchain.chat_models.openai.ChatOpenAI",
                        "config": {
                            "verbose": True,
                        },
                    },
                    "chat_memory": {
                        "class_path": "langchain.memory.RedisChatMessageHistory",
                        "config": {
                            "url": "redis://redis:6379/0",
                            "session": {"scope": "chat"},
                        },
                    },
                },
            },
        ],
        "prompt": {
            "class_path": "langchain.prompts.chat.ChatPromptTemplate",
            "config": {
                "messages": [
                    {
                        "role": "system",
                        "template": PIRATE_PROMPT,
                        "input_variables": ["related_artifacts", "chat_summary"],
                    },
                    {
                        "role": "user",
                        "template": "{user_input}",
                        "input_variables": ["user_input"],
                    },
                ],
            },
        },
    },
}

PIRATE_CHAIN_V1 = "b7d8f662-12f6-4525-b07b-c9ea7c10004c"
PIRATE_AGENT_V1 = "b7d8f662-12f6-4525-b07b-c9ea7c10004a"


class Command(BaseCommand):
    help = "Creates pirate agent v1"

    def handle(self, *args, **options):
        chain, _ = Chain.objects.get_or_create(
            pk=PIRATE_CHAIN_V1,
            defaults=dict(
                name="Pirate chain",
                description="Chain used for pirate agent v1",
            ),
        )
        chain.clear_chain()
        ChainNode.objects.create_from_config(chain=chain, root=True, config=PIRATE)

        Agent.objects.get_or_create(
            id=PIRATE_AGENT_V1,
            defaults=dict(
                name="Pirate",
                alias="pirate",
                purpose="responds to all inquiries with pirate talk",
                chain=chain,
                config={},
            ),
        )
