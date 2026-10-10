from django.core.management.base import BaseCommand

from ix.agents.models import Agent
from ix.chains.models import ChainNode, Chain

# Prompt includes variables for both ArtifactMemory and ConversationSummaryBufferMemory
TOOL_FORGE_PROMPT = '''
You are a prompt writer. You write prompts that generate Tool classes for user requests.

{related_artifacts}

CHAT_SUMMARY:
{chat_summary}

OUTPUT:
from typing import Optional
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun
)
from langchain.tools.base import BaseTool

class NameTool(BaseTool):
    """LangChain tool for [short description]."""

    name = "Name"
    description = (
        "[3-5 sentence explanation]"
    )
    
    # If the tool requires API keys or other parameters add fields here.
    api_key: str
    
    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the [name] tool asynchronously."""
        
        [async implementation]
'''

# Pirate chain config includes two memory classes that are combined automatically
# by the Ix loader using `langchain.memory.CombinedMemory`
TOOL_FORGE = {
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
                            "session_scope": "chat",
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
