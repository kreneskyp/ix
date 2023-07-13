from django.core.management.base import BaseCommand

from ix.chains.fixture_src.agents import AGENTS
from ix.chains.fixture_src.artifacts import ARTIFACT_MEMORY, SAVE_ARTIFACT
from ix.chains.fixture_src.chains import (
    LLM_CHAIN,
    LLM_TOOL_CHAIN,
    LLM_REPLY,
)
from ix.chains.fixture_src.chat_memory_backend import (
    FILESYSTEM_MEMORY_BACKEND,
    REDIS_MEMORY_BACKEND,
)
from ix.chains.fixture_src.embeddings import (
    OPENAI_EMBEDDINGS,
    GOOGLE_PALM_EMBEDDINGS,
    LLAMA_CPP_EMBEDDINGS,
    VERTEXAI_EMBEDDINGS,
    HUGGINGFACE_EMBEDDINGS,
    MOSAICML_INSTRUCTOR_EMBEDDINGS,
)
from ix.chains.fixture_src.ix import CHAT_MODERATOR_TYPE
from ix.chains.fixture_src.llm import OPENAI_LLM, GOOGLE_PALM, ANTHROPIC_LLM
from ix.chains.fixture_src.memory import (
    CONVERSATION_BUFFER_MEMORY,
    CONVERSATION_SUMMARY_BUFFER_MEMORY,
    CONVERSATION_BUFFER_WINDOW_MEMORY,
    CONVERSATION_TOKEN_BUFFER_MEMORY,
)
from ix.chains.fixture_src.openai_functions import (
    FUNCTION_SCHEMA,
    FUNCTION_OUTPUT_PARSER,
    OPENAPI_CHAIN,
)
from ix.chains.fixture_src.prompts import CHAT_PROMPT_TEMPLATE
from ix.chains.fixture_src.routing import SEQUENCE, MAP_SUBCHAIN
from ix.chains.fixture_src.testing import MOCK_MEMORY, MOCK_CHAIN
from ix.chains.fixture_src.tools import TOOLS
from ix.chains.fixture_src.vectorstores import REDIS_VECTORSTORE
from ix.chains.models import NodeType

COMPONENTS = []

# Embeddings
COMPONENTS.extend(
    [
        OPENAI_EMBEDDINGS,
        GOOGLE_PALM_EMBEDDINGS,
        LLAMA_CPP_EMBEDDINGS,
        VERTEXAI_EMBEDDINGS,
        HUGGINGFACE_EMBEDDINGS,
        MOSAICML_INSTRUCTOR_EMBEDDINGS,
    ]
)

# Agents
COMPONENTS.extend(AGENTS)
COMPONENTS.extend(TOOLS)

# LLMS
COMPONENTS.extend(
    [
        OPENAI_LLM,
        GOOGLE_PALM,
        ANTHROPIC_LLM,
    ]
)

# Chains
COMPONENTS.extend(
    [
        LLM_CHAIN,
        LLM_TOOL_CHAIN,
        LLM_REPLY,
        SEQUENCE,
        MAP_SUBCHAIN,
    ]
)

# OpenAI Functions
COMPONENTS.extend(
    [
        FUNCTION_SCHEMA,
        FUNCTION_OUTPUT_PARSER,
        OPENAPI_CHAIN,
    ]
)

# Prompts
COMPONENTS.extend(
    [
        CHAT_PROMPT_TEMPLATE,
    ]
)

# Memory
COMPONENTS.extend(
    [
        CONVERSATION_BUFFER_MEMORY,
        CONVERSATION_BUFFER_WINDOW_MEMORY,
        CONVERSATION_SUMMARY_BUFFER_MEMORY,
        CONVERSATION_TOKEN_BUFFER_MEMORY,
    ]
)

# Memory Backends
COMPONENTS.extend(
    [
        REDIS_MEMORY_BACKEND,
        FILESYSTEM_MEMORY_BACKEND,
    ]
)

# Vectorstores
COMPONENTS.extend(
    [
        REDIS_VECTORSTORE,
    ]
)

# IX Misc
COMPONENTS.extend([CHAT_MODERATOR_TYPE])

# IX Artifacts
COMPONENTS.extend(
    [
        ARTIFACT_MEMORY,
        SAVE_ARTIFACT,
    ]
)

# Testing
COMPONENTS.extend(
    [
        MOCK_MEMORY,
        MOCK_CHAIN,
    ]
)


class Command(BaseCommand):
    """
    Imports LangChain components from python fixtures. This is used to
    generate the initial set of components in the database. This method
    creates and updates components based on the class_path field.

    This loader is preferred to json fixtures because it allows for
    python constants and functions to be used to build the fixtures.

    This data this command loads is used to generate the json fixtures
    required for tests.
    """

    help = "Imports LangChain components from python fixtures."

    def handle(self, *args, **options):
        for component in COMPONENTS:
            class_path = component.get("class_path")
            if NodeType.objects.filter(class_path=class_path).exists():
                # updating existing node type
                print(f"Updating component: {component['class_path']}")
                node_type = NodeType.objects.get(class_path=class_path)
                for key, value in component.items():
                    if key == "class_path":
                        continue
                    setattr(node_type, key, value)
                node_type.save()
            else:
                # creating new node type
                NodeType.objects.create(**component)
