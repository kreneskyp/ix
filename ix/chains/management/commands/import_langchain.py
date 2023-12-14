from django.core.management.base import BaseCommand

from ix.api.components.types import NodeType as NodeTypePydantic
from ix.chains.fixture_src.agent_interaction import AGENT_INTERACTION_CHAINS

from ix.chains.fixture_src.agents import AGENTS
from ix.chains.fixture_src.artifacts import ARTIFACTS
from ix.chains.fixture_src.chains import CHAINS
from ix.chains.fixture_src.dalle import DALLE
from ix.chains.fixture_src.chat_memory_backend import MEMORY_BACKEND
from ix.chains.fixture_src.document_loaders import DOCUMENT_LOADERS
from ix.chains.fixture_src.embeddings import EMBEDDINGS
from ix.chains.fixture_src.flow import FLOW
from ix.chains.fixture_src.ix import CHAT_MODERATOR_TYPE
from ix.chains.fixture_src.json import JSON
from ix.chains.fixture_src.lcel import LANGCHAIN_RUNNABLES
from ix.chains.fixture_src.llm import LLMS
from ix.chains.fixture_src.memory import MEMORY
from ix.chains.fixture_src.openai_functions import OPENAI_FUNCTIONS
from ix.chains.fixture_src.parsers import PARSERS
from ix.chains.fixture_src.prompts import CHAT_PROMPT_TEMPLATE
from ix.chains.fixture_src.retriever import RETRIEVERS
from ix.chains.fixture_src.routing import ROUTING_CHAINS
from ix.chains.fixture_src.testing import MOCK_MEMORY, MOCK_CHAIN
from ix.chains.fixture_src.text_splitter import TEXT_SPLITTERS
from ix.chains.fixture_src.toolkit import TOOLKITS
from ix.chains.fixture_src.tools import TOOLS
from ix.chains.fixture_src.vectorstores import VECTORSTORES
from ix.chains.models import NodeType
from ix.chains.tests.mock_runnable import MOCK_RUNNABLE_CONFIG
from ix.secrets.models import SecretType

COMPONENTS = []

# Embeddings
COMPONENTS.extend(EMBEDDINGS)

# Agents
COMPONENTS.extend(AGENTS)
COMPONENTS.extend(TOOLS)
COMPONENTS.extend(TOOLKITS)

# LLMS
COMPONENTS.extend(LLMS)
COMPONENTS.extend(DALLE)

# Chains
COMPONENTS.extend(CHAINS)
COMPONENTS.extend(ROUTING_CHAINS)

# OpenAI Functions
COMPONENTS.extend(OPENAI_FUNCTIONS)

# Prompts
COMPONENTS.extend(
    [
        CHAT_PROMPT_TEMPLATE,
    ]
)

# Memory
COMPONENTS.extend(MEMORY)
COMPONENTS.extend(MEMORY_BACKEND)

# Document retrieval
COMPONENTS.extend(PARSERS)
COMPONENTS.extend(TEXT_SPLITTERS)
COMPONENTS.extend(DOCUMENT_LOADERS)
COMPONENTS.extend(VECTORSTORES)
COMPONENTS.extend(RETRIEVERS)

# IX LCEL integrations & flow
COMPONENTS.extend(LANGCHAIN_RUNNABLES)
COMPONENTS.extend(JSON)
COMPONENTS.extend(FLOW)

# IX Misc
COMPONENTS.extend([CHAT_MODERATOR_TYPE])
COMPONENTS.extend(AGENT_INTERACTION_CHAINS)

# IX Artifacts
COMPONENTS.extend(ARTIFACTS)

# Testing
COMPONENTS.extend(
    [
        MOCK_MEMORY,
        MOCK_CHAIN,
        MOCK_RUNNABLE_CONFIG,
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

    def to_stdout(self, msg):
        self.stdout.write(msg)

    def handle(self, *args, **options):
        for component in COMPONENTS:
            # validate by converting to pydantic model instance
            # TODO: COMPONENTS should be converted to pydantic models but for now
            #       expect that they are dicts and validated here.
            node_type_pydantic = NodeTypePydantic(**component)
            config_schema = node_type_pydantic.get_config_schema()
            validated_options = node_type_pydantic.model_dump(
                exclude={"id", "display_groups", "config_schema"}
            )

            class_path = component.get("class_path")
            if NodeType.objects.filter(class_path=class_path).exists():
                # updating existing node type
                self.to_stdout(f"Updating component: {class_path}")
                node_type = NodeType.objects.get(class_path=class_path)
                for key, value in validated_options.items():
                    if key == "class_path":
                        continue
                    setattr(node_type, key, value)
                node_type.config_schema = config_schema
                node_type.save()
            else:
                # creating new node type
                NodeType.objects.create(
                    config_schema=config_schema, **validated_options
                )

            # Secrets - generate SecretTypes from secret fields
            for secret_group in node_type_pydantic.secret_groups:
                try:
                    secret_type = SecretType.objects.get(name=secret_group.key)
                except SecretType.DoesNotExist:
                    secret_type = SecretType(name=secret_group.key)
                secret_type.fields_schema = secret_group.fields_schema
                secret_type.save()
