import uuid
from copy import deepcopy

import pytest
from unittest.mock import MagicMock

from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts.chat import ChatPromptValue
from langchain.schema.runnable import (
    RunnableSequence,
    RunnableMap,
    RunnableBranch,
    RunnableLambda,
)
from langchain.schema.runnable.base import RunnableEach
from langchain.text_splitter import TextSplitter
from langchain.vectorstores import Redis

from ix.chains.fixture_src.agents import OPENAI_FUNCTIONS_AGENT_CLASS_PATH
from ix.chains.fixture_src.lcel import (
    RUNNABLE_MAP_CLASS_PATH,
    RUNNABLE_BRANCH_CLASS_PATH,
)
from ix.chains.loaders.context import IxContext
from langchain.agents import AgentExecutor
from langchain.base_language import BaseLanguageModel
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryBufferMemory,
    CombinedMemory,
)
from langchain.schema import (
    BaseChatMessageHistory,
    BaseMemory,
    AIMessage,
    SystemMessage,
)
from langchain.tools import BaseTool

from ix.chains.fixture_src.tools import GOOGLE_SEARCH
from ix.chains.loaders.core import (
    aload_chain_flow,
    BranchPlaceholder,
    MapPlaceholder,
    ainit_chain_flow,
    SequencePlaceholder,
    ImplicitJoin,
)
from ix.chains.loaders.memory import get_memory_session
from ix.chains.loaders.text_splitter import TextSplitterShim
from ix.chains.loaders.tools import extract_tool_kwargs
from ix.chains.models import Chain
from ix.chains.tests.mock_configs import (
    CONVERSATIONAL_RETRIEVAL_CHAIN,
    EMBEDDINGS,
    LANGUAGE_PARSER,
    DOCUMENT_LOADER,
    TEST_DOCUMENTS,
    GOOGLE_SEARCH_CONFIG,
    MEMORY,
    LLM_REPLY_WITH_HISTORY,
    MEMORY_WITH_BACKEND,
    MEMORY_WITH_SCOPE,
    MEMORY_WITH_LLM,
    AGENT_MEMORY,
    REDIS_VECTORSTORE,
    OPENAI_LLM,
    PROMPT_CHAT,
    PROMPT_CHAT_0,
    PROMPT_CHAT_1,
    PROMPT_CHAT_2,
)
from ix.chains.tests.mock_memory import MockMemory
from ix.chains.tests.mock_runnable import MockRunnable
from ix.chains.tests.test_templates import TEXT_SPLITTER
from ix.conftest import aload_fixture
from ix.memory.artifacts import ArtifactMemory
from ix.runnable.ix import IxNode
from ix.task_log.tests.fake import afake_chain_node, afake_chain, afake_chain_edge
from ix.utils.importlib import import_class


class TestLoadLLM:
    pass


@pytest.mark.django_db
class TestLoadMemory:
    def test_load_memory(self, load_chain):
        instance = load_chain(MEMORY)
        assert isinstance(instance, ConversationBufferMemory)

    def test_load_multiple(self, load_chain, mock_openai_key):
        """Test loading multiple memories into a CombinedMemory"""
        MEMORY2 = deepcopy(MEMORY)
        MEMORY2["config"]["memory_key"] = "chat_history2"

        LLM_CONFIG = deepcopy(LLM_REPLY_WITH_HISTORY)
        LLM_CONFIG["config"]["memory"] = [MEMORY, MEMORY2]
        ix_node = load_chain(LLM_CONFIG)
        chain = ix_node.child
        instance = chain.memory
        assert isinstance(instance, CombinedMemory)
        assert len(instance.memories) == 2
        assert instance.memories[0].memory_key == "chat_history"
        assert instance.memories[1].memory_key == "chat_history2"

    def test_load_backend(self, load_chain):
        """
        A memory class can have a backend that separates memory logic from
        the storage system. ChatMemory works this way.
        """
        instance = load_chain(MEMORY_WITH_BACKEND)
        assert isinstance(instance, ConversationBufferMemory)
        assert isinstance(instance.chat_memory, BaseChatMessageHistory)

    def test_load_memory_with_scope(self, chat, load_chain):
        """
        Test loading with a scope.

        Not all memories support sessions, for example ChatMemory
        adds scoping to the backend.
        """
        chat = chat["chat"]
        chat_id = chat.task.leading_chats.first().id
        instance = load_chain(MEMORY_WITH_SCOPE)
        assert isinstance(instance, ArtifactMemory)
        assert instance.session_id == f"tests_chat_{chat_id}"

    def test_load_llm(self, load_chain, mock_openai):
        """
        Memory classes may optionally load an llm. (e.g. SummaryMemory)
        """
        instance = load_chain(MEMORY_WITH_LLM)
        assert isinstance(instance, ConversationSummaryBufferMemory)
        assert isinstance(instance.llm, BaseLanguageModel)

    def test_load_class_with_config(self, chat, mocker, load_chain):
        """
        Test loading a class whose config is defined in MEMORY_CLASSES.
        This tests configuring an external class with the required config
        to integrate into Ix
        """
        chat = chat["chat"]
        chat_id = chat.task.leading_chats.first().id

        # patch MEMORY_CLASSES to setup the test
        from ix.chains.loaders import memory

        mock_memory_classes = {
            MockMemory: {
                "supports_session": True,
            }
        }
        mocker.patch.object(memory, "MEMORY_CLASSES", mock_memory_classes)

        # load a memory that will use the mock class config
        instance = load_chain(
            {
                "class_path": "ix.chains.tests.mock_memory.MockMemory",
                "config": {
                    "session_scope": "chat",
                    "session_prefix": "tests",
                },
            },
        )
        assert isinstance(instance, MockMemory)
        assert instance.session_id == f"tests_chat_{chat_id}"


@pytest.mark.django_db
class TestLoadChatMemoryBackend:
    def test_load_chat_memory_backend(self, chat, load_chain):
        chat = chat["chat"]
        chat_id = chat.task.leading_chats.first().id

        # Config
        config = {
            "class_path": "langchain.memory.RedisChatMessageHistory",
            "config": {
                "url": "redis://redis:6379/0",
                "session_scope": "chat",
                "session_prefix": "tests",
            },
        }

        # Run
        backend = load_chain(config)
        assert backend.session_id == f"tests_chat_{chat_id}"

    def test_load_defaults(self, chat, load_chain):
        """
        ChatMemoryBackend should always load session_id. If `session` isn't present then
        load the `chat` scope by default.
        """
        chat = chat["chat"]
        chat_id = chat.task.leading_chats.first().id

        # Config
        config = {
            "class_path": "langchain.memory.RedisChatMessageHistory",
            "config": {
                "url": "redis://redis:6379/0",
            },
        }

        # Run
        backend = load_chain(config)
        assert backend.session_id == f"chat_{chat_id}"


@pytest.mark.django_db
class TestGetMemorySession:
    """Test parsing the session scope from the chain config and runtime context."""

    @pytest.mark.parametrize(
        "config, cls, expected",
        [
            # No scope - defaults to chat
            (
                {
                    "session_scope": "",
                    "session_prefix": "123",
                    "session_key": "session_id",
                },
                BaseChatMessageHistory,
                ("123_chat_1000", "session_id"),
            ),
            (
                {
                    "session_scope": None,
                    "session_prefix": "123",
                    "session_key": "session_id",
                },
                BaseChatMessageHistory,
                ("123_chat_1000", "session_id"),
            ),
            (
                {"session_prefix": "123", "session_key": "session_id"},
                BaseChatMessageHistory,
                ("123_chat_1000", "session_id"),
            ),
            # agent, task, user scopes
            (
                {
                    "session_scope": "agent",
                    "session_prefix": "456",
                    "session_key": "session_id",
                },
                BaseMemory,
                ("456_agent_1001", "session_id"),
            ),
            (
                {
                    "session_scope": "task",
                    "session_prefix": "789",
                    "session_key": "session_id",
                },
                BaseMemory,
                ("789_task_1002", "session_id"),
            ),
            (
                {
                    "session_scope": "user",
                    "session_prefix": "321",
                    "session_key": "session_id",
                },
                BaseChatMessageHistory,
                ("321_user_1003", "session_id"),
            ),
            # custom session_id_key
            (
                {"session_scope": "chat", "session_key": "chat_session"},
                BaseChatMessageHistory,
                ("chat_1000", "chat_session"),
            ),
            # no session prefix
            (
                {"session_scope": "chat", "session_key": "session_id"},
                BaseChatMessageHistory,
                ("chat_1000", "session_id"),
            ),
            # custom session prefix
            (
                {"session_scope": "chat", "session_prefix": "static_session_id"},
                BaseChatMessageHistory,
                ("static_session_id_chat_1000", "session_id"),
            ),
        ],
    )
    def test_get_memory_session(self, task, config, cls, expected):
        """Test various scope configurations."""
        context = MagicMock()
        context.task = task
        context.chat_id = "1000"
        context.agent_id = "1001"
        context.task_id = "1002"
        context.user_id = "1003"

        result = get_memory_session(config, context, cls)
        assert result == expected

    def test_parse_scope_unsupported_scope(self, task):
        config = {
            "session_scope": "unsupported_scope",
            "session_id": "123",
            "session_id_key": "session_id",
        }
        cls = BaseChatMessageHistory
        context = IxContext.from_task(task=task)
        with pytest.raises(ValueError) as excinfo:
            get_memory_session(config, context, cls)
        assert "unknown scope" in str(excinfo.value)


class TestLoadChain:
    def test_load_chain(self):
        pass


class TestExtractToolKwargs:
    @pytest.fixture
    def kwargs(self):
        return {
            "return_direct": False,
            "verbose": False,
            "tool_key1": "tool_value1",
            "tool_key2": "tool_value2",
        }

    def test_extract_tool_kwargs_returns_dict(self, kwargs):
        result = extract_tool_kwargs(kwargs)
        assert isinstance(result, dict)

    def test_extract_tool_kwargs_only_includes_tool_kwargs(self, kwargs):
        node_kwargs = kwargs.copy()
        tool_kwargs = extract_tool_kwargs(node_kwargs)
        expected_node_kwargs = {"tool_key1": "tool_value1", "tool_key2": "tool_value2"}
        expected_tool_kwargs = {
            "return_direct": False,
            "verbose": False,
        }
        assert tool_kwargs == expected_tool_kwargs
        assert expected_node_kwargs == node_kwargs


@pytest.fixture()
def mock_google_api_key(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "MOCK_KEY")
    monkeypatch.setenv("GOOGLE_CSE_ID", "MOCK_ID")


@pytest.mark.django_db
class TestGoogleTools:
    async def test_load_tools(self, aload_chain, mock_google_api_key):
        """Test that tools can be loaded."""
        config = {
            "class_path": GOOGLE_SEARCH["class_path"],
            "name": "tester",
            "description": "test",
            "config": {},
        }

        instance = await aload_chain(config)
        assert isinstance(instance, IxNode)
        assert isinstance(instance.child, BaseTool)


@pytest.mark.django_db
class TestLoadAgents:
    # list of known agents. This list may not be exhaustive
    # of all agents available since functions are dynamically
    # loaded from LangChain code.
    KNOWN_AGENTS = [
        "initialize_zero_shot_react_description",
        "initialize_conversational_react_description",
        "initialize_chat_zero_shot_react_description",
        "initialize_chat_conversational_react_description",
        "initialize_structured_chat_zero_shot_react_description",
        "initialize_openai_functions",
        "initialize_openai_multi_functions",
    ]

    def test_init_functions(self):
        """Test that agent init wrappers were generated."""
        from ix.chains.loaders.agents import FUNCTION_NAMES

        for name in self.KNOWN_AGENTS:
            assert name in FUNCTION_NAMES

    @pytest.mark.parametrize(
        "agent_name",
        [
            "initialize_zero_shot_react_description",
            "initialize_conversational_react_description",
            "initialize_chat_zero_shot_react_description",
            "initialize_chat_conversational_react_description",
            "initialize_structured_chat_zero_shot_react_description",
            "initialize_openai_functions",
            "initialize_openai_multi_functions",
        ],
    )
    async def test_load_agents(
        self, agent_name, aload_chain, mock_openai, mock_google_api_key
    ):
        """Test that agent can be loaded."""

        config = {
            "class_path": f"ix.chains.loaders.agents.{agent_name}",
            "name": "tester",
            "description": "test",
            "config": {"tools": [GOOGLE_SEARCH_CONFIG], "llm": OPENAI_LLM},
        }

        ix_node = await aload_chain(config)
        instance = ix_node.child
        assert isinstance(instance, AgentExecutor)

    async def test_agent_memory(self, mock_openai, aload_chain, mock_google_api_key):
        config = {
            "class_path": OPENAI_FUNCTIONS_AGENT_CLASS_PATH,
            "name": "tester",
            "description": "test",
            "config": {
                "tools": [GOOGLE_SEARCH_CONFIG],
                "llm": OPENAI_LLM,
                "memory": AGENT_MEMORY,
            },
        }
        ix_node = await aload_chain(config)
        executor = ix_node.child
        assert isinstance(executor, AgentExecutor)  # sanity check

        # 1. test that prompt includes placeholders
        # 2. test that memory keys are correct
        # 3. test that memory is loaded for agent
        result = await executor.acall(inputs={"input": "foo", "user_input": "bar"})

        # verify response contains memory
        assert result["chat_history"][0].content == "bar"
        assert result["chat_history"][1].content == "mock llm response"

        # call second time to smoke test
        await executor.acall(inputs={"input": "foo", "user_input": "bar"})

    async def test_agent_memory_misconfigured(
        self, mock_openai, aload_chain, mock_google_api_key
    ):
        """test agent/memory misconfigurations that should raise errors
        - memory class must have `return_messages=True`
        """
        config = {
            "class_path": "ix.chains.loaders.agents.initialize_zero_shot_react_description",
            "name": "tester",
            "description": "test",
            "config": {
                "tools": [GOOGLE_SEARCH_CONFIG],
                "llm": OPENAI_LLM,
                "memory": MEMORY,
            },
        }
        with pytest.raises(ValueError) as excinfo:
            await aload_chain(config)
            assert "Agents require return_messages=True" in str(excinfo.value)


@pytest.mark.django_db
class TestLoadRetrieval:
    """Test loading retrieval components.

    This is a test of loading mechanism for the various retrieval components.
    It is not an exhaustive test that all retrieval components work as expected.
    The tests verify that any special loading logic for the components is working.
    """

    async def test_load_language_parser(self, aload_chain):
        component = await aload_chain(LANGUAGE_PARSER)
        assert isinstance(component, LanguageParser)
        assert component.language == "python"

    async def test_load_document_loader(self, aload_chain):
        component = await aload_chain(DOCUMENT_LOADER)
        assert isinstance(component, GenericLoader)
        assert isinstance(component.blob_parser, LanguageParser)

        # non-exhaustive test of document loading
        documents = component.load()
        sources = {doc.metadata["source"] for doc in documents}
        expected_sources = {
            str(TEST_DOCUMENTS / "foo.py"),
            str(TEST_DOCUMENTS / "bar.py"),
        }
        assert sources == expected_sources

    async def test_load_text_splitter(self, aload_chain):
        component = await aload_chain(TEXT_SPLITTER)
        assert isinstance(component, TextSplitterShim)
        assert isinstance(component.document_loader, GenericLoader)
        assert isinstance(component.text_splitter, TextSplitter)

        # sanity check that the splitter splits text
        # does not test the actual splitting algorithm
        with open(TEST_DOCUMENTS / "foo.py", "r") as foo_file:
            foo_content = foo_file.read()
        split_texts = component.text_splitter.split_text(foo_content)
        assert len(split_texts) >= 1

    async def test_load_embeddings(self, aload_chain):
        component = await aload_chain(EMBEDDINGS)
        assert isinstance(component, OpenAIEmbeddings)

    async def test_load_vectorstore(
        self, clean_redis, aload_chain, mock_openai_embeddings
    ):
        component = await aload_chain(REDIS_VECTORSTORE)
        assert isinstance(component, Redis)

    async def test_load_conversational_chain(
        self, clean_redis, aload_chain, mock_openai_embeddings
    ):
        """Test loading a fully configured conversational chain."""
        ix_node = await aload_chain(CONVERSATIONAL_RETRIEVAL_CHAIN)
        component = ix_node.child
        assert isinstance(component, ConversationalRetrievalChain)


@pytest.mark.django_db
class TestFlowComponents:
    """Testing flow components: sequences, maps, branches, eachs, etc."""

    async def assert_basic_sequence(self, runnable: RunnableSequence):
        # TODO: it's not coming back as runnable sequence
        assert isinstance(runnable, RunnableSequence)
        assert len(runnable.steps) == 2
        assert isinstance(
            runnable.steps[0].child, import_class(PROMPT_CHAT["class_path"])
        )
        assert isinstance(
            runnable.steps[1].child, import_class(OPENAI_LLM["class_path"])
        )

        # test invoking chain
        output = await runnable.ainvoke(input={"user_input": "hello!"})
        assert output == AIMessage(content="mock llm response")

    async def test_basic_sequence(self, anode_types, aix_context, mock_openai):
        """Testing a basic flow loaded from node graph.

        chat_input -> prompt -> LLM -> output
        """
        chain = await afake_chain()
        prompt = await afake_chain_node(chain=chain, root=True, config=PROMPT_CHAT)
        llm = await afake_chain_node(chain=chain, config=OPENAI_LLM, root=False)
        await afake_chain_edge(chain=chain, source=prompt, target=llm, relation="LINK")

        runnable = await chain.aload_chain(context=aix_context)
        await self.assert_basic_sequence(runnable)

    async def test_parallel(self, aix_context, mock_openai):
        """Test creating a RunnableParallel from node graph."""

        foo_hash = str(uuid.uuid4())
        bar_hash = str(uuid.uuid4())
        RUNNABLE_MAP = {
            "class_path": RUNNABLE_MAP_CLASS_PATH,
            "config": {
                "steps": ["foo", "bar"],
                "steps_hash": [foo_hash, bar_hash],
            },
        }

        chain = await afake_chain()
        runnable_map = await afake_chain_node(
            chain=chain, root=False, config=RUNNABLE_MAP
        )
        prompt0 = await afake_chain_node(chain=chain, root=True, config=PROMPT_CHAT_0)
        prompt1 = await afake_chain_node(chain=chain, root=True, config=PROMPT_CHAT_1)
        await afake_chain_edge(
            chain=chain,
            source=prompt0,
            target=runnable_map,
            relation="LINK",
            source_key="out",
            target_key=foo_hash,
        )
        await afake_chain_edge(
            chain=chain,
            source=prompt1,
            target=runnable_map,
            relation="LINK",
            source_key="out",
            target_key=bar_hash,
        )

        # test loaded runnable
        runnable = await chain.aload_chain(context=aix_context)
        assert isinstance(runnable, RunnableMap)
        assert len(runnable.steps) == 2
        assert isinstance(
            runnable.steps["foo"].child, import_class(PROMPT_CHAT_0["class_path"])
        )
        assert isinstance(
            runnable.steps["bar"].child, import_class(PROMPT_CHAT_1["class_path"])
        )

        # test invoking chain
        output = await runnable.ainvoke(input={"input": "hello!"})
        assert output == {
            "bar": ChatPromptValue(messages=[SystemMessage(content="You are bot 1.")]),
            "foo": ChatPromptValue(messages=[SystemMessage(content="You are bot 0.")]),
        }

    async def test_branch(self, aix_context, mock_openai):
        foo_uuid = str(uuid.uuid4())
        bar_uuid = str(uuid.uuid4())

        RUNNABLE_BRANCH = {
            "class_path": RUNNABLE_BRANCH_CLASS_PATH,
            "config": {
                "branches": ["foo", "bar"],
                "branches_hash": [foo_uuid, bar_uuid],
            },
        }

        chain = await afake_chain()
        runnable_branch = await afake_chain_node(
            chain=chain, root=True, config=RUNNABLE_BRANCH
        )
        prompt0 = await afake_chain_node(chain=chain, root=False, config=PROMPT_CHAT_0)
        prompt1 = await afake_chain_node(chain=chain, root=False, config=PROMPT_CHAT_1)
        prompt2 = await afake_chain_node(chain=chain, root=False, config=PROMPT_CHAT_2)
        await afake_chain_edge(
            chain=chain,
            source=runnable_branch,
            target=prompt0,
            relation="LINK",
            source_key="default",
            target_key="in",
        )
        await afake_chain_edge(
            chain=chain,
            source=runnable_branch,
            target=prompt1,
            relation="LINK",
            source_key=foo_uuid,
            target_key="in",
        )
        await afake_chain_edge(
            chain=chain,
            source=runnable_branch,
            target=prompt2,
            relation="LINK",
            source_key=bar_uuid,
            target_key="in",
        )

        runnable = await chain.aload_chain(context=aix_context)
        assert isinstance(runnable, RunnableBranch)
        assert len(runnable.branches) == 2
        assert isinstance(runnable.default, IxNode)
        assert isinstance(
            runnable.default.child, import_class(PROMPT_CHAT_0["class_path"])
        )
        assert isinstance(runnable.branches[0][0], RunnableLambda)
        assert isinstance(
            runnable.branches[0][1].child, import_class(PROMPT_CHAT_1["class_path"])
        )
        assert isinstance(runnable.branches[1][0], RunnableLambda)
        assert isinstance(
            runnable.branches[1][1].child, import_class(PROMPT_CHAT_2["class_path"])
        )

        # test invoking chain
        output = await runnable.ainvoke(input={"input": "hello!"})
        assert output == ChatPromptValue(
            messages=[SystemMessage(content="You are bot 0.")]
        )
        output = await runnable.ainvoke(input={"foo": True})
        assert output == ChatPromptValue(
            messages=[SystemMessage(content="You are bot 1.")]
        )
        output = await runnable.ainvoke(input={"bar": True})
        assert output == ChatPromptValue(
            messages=[SystemMessage(content="You are bot 2.")]
        )

    async def test_each(self, aix_context, mock_openai, lcel_flow_each_in_sequence):
        """Test RunnableEach"""
        chain = lcel_flow_each_in_sequence["chain"]
        runnable = await chain.aload_chain(context=aix_context)
        assert isinstance(runnable, RunnableSequence)
        assert len(runnable.steps) == 2
        assert isinstance(runnable.steps[0], IxNode)
        assert isinstance(runnable.steps[0].child, RunnableEach)
        assert isinstance(runnable.steps[1], IxNode)
        assert isinstance(runnable.steps[1].child, MockRunnable)

        output = await runnable.ainvoke(input=["one", "two", "three"])
        assert output == {
            "input": [
                {"input": "one", "node1": 0},
                {"input": "two", "node1": 0},
                {"input": "three", "node1": 0},
            ],
            "node2": 0,
        }


MOCK_PLAN_RESPONSE = dict(name="plan_coding", arguments={"agent_id": 1})


@pytest.mark.skip(reason="Test is having an issue with the return type.")
@pytest.mark.django_db
class TestRunnableBinding:
    async def test_bind_functions(self, anode_types, aix_context, mock_openai):
        """Test a flow with plan agent"""
        await aload_fixture("agent/plan")
        chain = await Chain.objects.aget(agent__alias="plan")

        # test loaded flow
        await aload_chain_flow(chain)

        # init flow
        runnable = await ainit_chain_flow(chain, context=aix_context)
        output = await runnable.ainvoke(input={"user_input": "code a fizzbuzz"})

        # HAX: using standard mocked response
        assert output == {
            "user_input": "test",
            "chat_output": MOCK_PLAN_RESPONSE,
        }


@pytest.mark.django_db
class TestLoadFlow:
    """
    Tests that validate loading various configurations of LCEL flows constructed
    by nodes & edges in the database can be loaded into the intermediate data structures
    needed to convert them into Runnable components.

    These tests construct nodes & edges then validate the loaded placeholder flow.
    These tests do not init or invoke the loaded flows.
    The intent is just to validate the intermediate structures.
    """

    async def test_sequence(self, lcel_sequence, aix_context):
        fixture = lcel_sequence
        chain = fixture["chain"]
        flow = await aload_chain_flow(chain)

        assert flow == [
            fixture["nodes"][0],
            fixture["nodes"][1],
        ]

    async def test_map(self, lcel_map, aix_context):
        """Test a map from the start of a chain"""
        fixture = lcel_map
        chain = fixture["chain"]

        # assert state of fixture
        assert isinstance(fixture["map"], MapPlaceholder)
        assert len(fixture["map"].map) == 2
        assert fixture["map"].map == {
            "a": fixture["node1"],
            "b": fixture["node2"],
        }
        # assert flow
        flow = await aload_chain_flow(chain)
        assert flow == fixture["map"]

    async def test_map_with_one_branch(self, lcel_map_with_one_branch, aix_context):
        fixture = lcel_map_with_one_branch
        chain = fixture["chain"]

        # assert state of fixture
        assert isinstance(fixture["map"], MapPlaceholder)
        assert fixture["map"].map == {
            "a": fixture["node1"],
        }
        # assert flow
        flow = await aload_chain_flow(chain)
        assert flow == fixture["map"]

    async def test_sequence_in_map_start(self, lcel_sequence_in_map_start, aix_context):
        """Test a map with a nested sequence. First node in chain is the map."""
        fixture = lcel_sequence_in_map_start
        chain = fixture["chain"]
        flow = await aload_chain_flow(chain)
        assert flow == fixture["map"]

    async def test_sequence_in_map_in_sequence(
        self, lcel_sequence_in_map_in_sequence, aix_context
    ):
        """Test a map containing a sequence, that is contained in a sequence.

        Tests that sequence_in_map works when the map is not the first node in the chain.
        """
        fixture = lcel_sequence_in_map_in_sequence
        chain = fixture["chain"]
        flow = await aload_chain_flow(chain)
        assert flow == [
            fixture["node1"],
            fixture["map"],
            fixture["node4"],
        ]

    async def test_sequence_in_map_in_sequence_n2(
        self, lcel_sequence_in_map_in_sequence_n2, aix_context
    ):
        """Test a map containing a sequence, that is contained in a sequence.

        Tests that sequence_in_map works when the map is not the first node in the chain.
        """
        fixture = lcel_sequence_in_map_in_sequence_n2
        chain = fixture["chain"]
        flow = await aload_chain_flow(chain)
        assert flow == [
            fixture["node1"],
            fixture["map"],
            fixture["node4"],
            fixture["node5"],
        ]

    async def test_map_in_sequence_start(self, lcel_map_in_sequence_start, aix_context):
        """Test a sequence starting with a map. First node in chain is a map"""
        fixture = lcel_map_in_sequence_start
        chain = fixture["chain"]
        flow = await aload_chain_flow(chain)
        assert flow == [
            fixture["map"],
            fixture["node2"],
        ]

    async def test_map_in_sequence_start_n2(
        self, lcel_map_in_sequence_start_n2, aix_context
    ):
        """Test a sequence starting with a map. First node in chain is a map"""
        fixture = lcel_map_in_sequence_start_n2
        chain = fixture["chain"]
        flow = await aload_chain_flow(chain)
        assert flow == [
            fixture["map"],
            fixture["node2"],
            fixture["node3"],
        ]

    async def test_map_in_sequence(self, lcel_map_in_sequence, aix_context):
        """Test a sequence with a nested map. First node in chain is the first node of sequence."""
        fixture = lcel_map_in_sequence
        chain = lcel_map_in_sequence["chain"]
        flow = await aload_chain_flow(chain)
        assert flow == [
            fixture["node1"],
            fixture["map"],
            fixture["node2"],
        ]

    async def test_map_in_sequence_n2(self, lcel_map_in_sequence_n2, aix_context):
        """Test a sequence with a nested map. First node in chain is the first node of sequence."""
        fixture = lcel_map_in_sequence_n2
        chain = fixture["chain"]
        flow = await aload_chain_flow(chain)
        assert flow == [
            fixture["node1"],
            fixture["map"],
            fixture["node2"],
            fixture["node3"],
        ]

    async def test_map_in_map(self, lcel_map_in_map, aix_context):
        """Test a map with a nested map"""
        fixture = lcel_map_in_map
        chain = fixture["chain"]
        flow = await aload_chain_flow(chain)
        assert flow == fixture["map"]

    async def test_map_in_map_in_sequence_start(
        self, lcel_map_in_map_in_sequence_start, aix_context
    ):
        """Test a map with a nested map"""
        fixture = lcel_map_in_map_in_sequence_start
        chain = fixture["chain"]
        flow = await aload_chain_flow(chain)
        assert flow == [
            fixture["map"],
            fixture["node3"],
        ]

    async def test_map_in_map_in_sequence_start_n2(
        self, lcel_map_in_map_in_sequence_start_n2, aix_context
    ):
        """Test a map with a nested map"""
        fixture = lcel_map_in_map_in_sequence_start_n2
        chain = fixture["chain"]
        flow = await aload_chain_flow(chain)
        assert flow == [
            fixture["map"],
            fixture["node3"],
            fixture["node4"],
        ]

    async def test_map_in_map_in_sequence(
        self, lcel_map_in_map_in_sequence, aix_context
    ):
        """Test a map with a nested map"""
        fixture = lcel_map_in_map_in_sequence
        chain = fixture["chain"]
        flow = await aload_chain_flow(chain)
        assert flow == [
            fixture["node1"],
            fixture["map"],
        ]

    async def test_map_in_map_in_sequence_n2(
        self, lcel_map_in_map_in_sequence_n2, aix_context
    ):
        """Test a map with a nested map"""
        fixture = lcel_map_in_map_in_sequence_n2
        chain = fixture["chain"]
        flow = await aload_chain_flow(chain)
        assert flow == [
            fixture["node1"],
            fixture["map"],
            fixture["node4"],
            fixture["node5"],
        ]

    async def test_branch(self, lcel_branch, aix_context):
        fixture = lcel_branch
        chain = fixture["chain"]

        # sanity check setup
        assert isinstance(fixture["branch"], BranchPlaceholder)
        assert fixture["branch"].default == fixture["node1"]
        assert fixture["branch"].branches == [
            ("a", fixture["node2"]),
            ("b", fixture["node3"]),
        ]

        # test loaded flow
        flow = await aload_chain_flow(chain)
        assert flow == fixture["branch"]

    async def test_branch_in_branch(self, lcel_branch_in_branch, aix_context):
        """Test a branch with a nested branch"""
        fixture = lcel_branch_in_branch
        chain = fixture["chain"]

        # sanity check setup
        assert isinstance(fixture["branch"], BranchPlaceholder)
        assert fixture["branch"].default == fixture["node5"]
        assert fixture["branch"].branches == [
            ("a", fixture["inner_branch"]),
            ("b", fixture["node4"]),
        ]

        # test loaded flow
        flow = await aload_chain_flow(chain)
        assert flow == fixture["branch"]

    async def test_branch_in_default_branch(
        self, lcel_branch_in_default_branch, aix_context
    ):
        """Test a branch with a nested branch"""
        fixture = lcel_branch_in_default_branch
        chain = fixture["chain"]

        # sanity check setup
        assert isinstance(fixture["branch"], BranchPlaceholder)
        assert fixture["branch"].default == fixture["inner_branch"]

        # test loaded flow
        flow = await aload_chain_flow(chain)
        assert flow == fixture["branch"]

    async def test_sequence_in_branch(self, lcel_sequence_in_branch, aix_context):
        """Test a branch with a nested sequence"""
        fixture = lcel_sequence_in_branch
        chain = fixture["chain"]

        # sanity check setup
        assert isinstance(fixture["branch"], BranchPlaceholder)
        assert fixture["branch"].branches == [
            ("a", fixture["inner_sequence"]),
            ("b", fixture["node1"]),
        ]

        # test loaded flow
        flow = await aload_chain_flow(chain)
        assert flow == fixture["branch"]

    async def test_sequence_in_default_branch(
        self, lcel_sequence_in_default_branch, aix_context
    ):
        """Test a branch with a nested sequence"""
        fixture = lcel_sequence_in_default_branch
        chain = fixture["chain"]

        # sanity check setup
        assert isinstance(fixture["branch"], BranchPlaceholder)
        assert fixture["branch"].default == fixture["inner_sequence"]

        # test loaded flow
        flow = await aload_chain_flow(chain)
        assert flow == fixture["branch"]

    async def test_map_in_branch(self, lcel_map_in_branch, aix_context):
        """Test a branch with a nested map"""
        fixture = lcel_map_in_branch
        chain = fixture["chain"]

        # test loaded flow
        flow = await aload_chain_flow(chain)
        assert flow == fixture["branch"]

    async def test_map_in_default_branch(self, lcel_map_in_default_branch, aix_context):
        """Test a branch with a nested map"""
        fixture = lcel_map_in_default_branch
        chain = fixture["chain"]

        # test loaded flow
        flow = await aload_chain_flow(chain)
        assert flow == fixture["branch"]

    async def test_branch_in_sequence(self, lcel_branch_in_sequence, aix_context):
        """Test a sequence with a nested branch.

        implicit maps are inherently flaky so this test requires manually checking
        the loaded flow.
        """
        fixture = lcel_branch_in_sequence
        chain = fixture["chain"]

        # test loaded flow
        flow = await aload_chain_flow(chain)

        # Verify the class of the flow using isinstance
        assert isinstance(flow, SequencePlaceholder)
        assert flow.steps[0] == fixture["node0"]
        assert isinstance(flow.steps[1], BranchPlaceholder)

        # default branch
        default = flow.steps[1].default
        assert isinstance(default, SequencePlaceholder)
        assert isinstance(default.steps[0], ImplicitJoin)
        assert default.steps[0].source == [fixture["node1"]]
        assert default.steps[0].target.node == fixture["node4"]
        assert default.steps[1] == fixture["node5"]

        # branch a
        label_a, branch_a = flow.steps[1].branches[0]
        assert label_a == "a"
        assert isinstance(branch_a, SequencePlaceholder)
        assert isinstance(branch_a.steps[0], ImplicitJoin)
        assert branch_a.steps[0].source == [fixture["node2"]]
        assert branch_a.steps[0].target.node == fixture["node4"]
        assert branch_a.steps[1] == fixture["node5"]

        # branch b
        label_b, branch_b = flow.steps[1].branches[1]
        assert label_b == "b"
        assert isinstance(branch_b, SequencePlaceholder)
        assert isinstance(branch_b.steps[0], ImplicitJoin)
        assert branch_b.steps[0].source == [fixture["node3"]]
        assert branch_b.steps[0].target.node == fixture["node4"]
        assert branch_b.steps[1] == fixture["node5"]

        # The maps are implicit maps so the mapped value isn't used but verifying
        # it was parsed as expected. This value is one of the source nodes randomly
        # based on the order the graph was parsed.
        assert default.steps[0].target.map["in"] in [
            fixture["node1"],
            fixture["node2"],
            fixture["node3"],
        ]
        assert branch_a.steps[0].target.map["in"] in [
            fixture["node1"],
            fixture["node2"],
            fixture["node3"],
        ]
        assert branch_b.steps[0].target.map["in"] in [
            fixture["node1"],
            fixture["node2"],
            fixture["node3"],
        ]

    @pytest.mark.skip(reason="not supported yet")
    async def test_branch_in_map_in_sequence(
        self, lcel_branch_in_map_in_sequence, aix_context
    ):
        fixture = lcel_branch_in_map_in_sequence
        chain = fixture["chain"]

        # test loaded flow
        flow = await aload_chain_flow(chain)
        assert flow == fixture["sequence"]

    @pytest.mark.skip(reason="not supported yet")
    async def test_branch_in_map_start(self, lcel_branch_in_map_start, aix_context):
        fixture = lcel_branch_in_map_start
        chain = fixture["chain"]

        # test loaded flow
        flow = await aload_chain_flow(chain)
        assert flow == fixture["map"]

    async def test_join_after_branch(self, lcel_join_after_branch, aix_context):
        """Test a join after a branch

        The join is two sequences that link to the same node/placeholder/component
        instance. This way when instantiated the chain only has one instance of
        the component.

                  |--> *: [node1]---|
        [branch]--+                 |
                  |--> a: [node2] --|
                  +                 +--> [node4] --> [node5]
                  |--> b: [node3] --|

        This is structured as separate sequences for both `a` and `b`, but `node4`
        and `node5` are the same component instance.

                  |--> *: [node1] --> [node4] --> [node5]
        [branch]--+
                  |--> a: [node2] --> [node4] --> [node5]
                  +
                  |--> b: [node3] --> [node4] --> [node5]
        """
        fixture = lcel_join_after_branch
        chain = fixture["chain"]

        # test loaded flow
        flow = await aload_chain_flow(chain)

        # root is a branch
        assert isinstance(flow, BranchPlaceholder)
        assert flow.node == fixture["branch_node"]

        # default branch
        default = flow.default
        assert isinstance(default, SequencePlaceholder)
        assert isinstance(default.steps[0], ImplicitJoin)
        assert default.steps[0].source == [fixture["node1"]]
        assert default.steps[0].target.node == fixture["node4"]
        assert default.steps[1] == fixture["node5"]

        # branch a
        label_a, branch_a = flow.branches[0]
        assert label_a == "a"
        assert isinstance(branch_a, SequencePlaceholder)
        assert isinstance(branch_a.steps[0], ImplicitJoin)
        assert branch_a.steps[0].source == [fixture["node2"]]
        assert branch_a.steps[0].target.node == fixture["node4"]
        assert branch_a.steps[1] == fixture["node5"]

        # branch b
        label_b, branch_b = flow.branches[1]
        assert label_b == "b"
        assert isinstance(branch_b, SequencePlaceholder)
        assert isinstance(branch_b.steps[0], ImplicitJoin)
        assert branch_b.steps[0].source == [fixture["node3"]]
        assert branch_b.steps[0].target.node == fixture["node4"]
        assert branch_b.steps[1] == fixture["node5"]

        # The maps are implicit maps so the mapped value isn't used but verifying
        # it was parsed as expected. This value is one of the source nodes randomly
        # based on the order the graph was parsed.
        assert default.steps[0].target.map["in"] in [
            fixture["node1"],
            fixture["node2"],
            fixture["node3"],
        ]
        assert branch_a.steps[0].target.map["in"] in [
            fixture["node1"],
            fixture["node2"],
            fixture["node3"],
        ]
        assert branch_b.steps[0].target.map["in"] in [
            fixture["node1"],
            fixture["node2"],
            fixture["node3"],
        ]

        # verify that the joined nodes are the same instances
        # HAX: disabling this since the optimization was disabled to support
        #      implicit joins
        # assert flow.branches[0][1][1] == fixture["node4"]
        # assert flow.branches[1][1][1] == fixture["node4"]
        # assert flow.branches[0][1][2] == fixture["node5"]
        # assert flow.branches[1][1][2] == fixture["node5"]

    async def test_each(self, lcel_flow_each):
        fixture = lcel_flow_each
        chain = fixture["chain"]

        # test loaded flow
        flow = await aload_chain_flow(chain)
        assert flow == fixture["each"]

    async def test_sequence_in_each(self, lcel_flow_each_sequence):
        fixture = lcel_flow_each_sequence
        chain = fixture["chain"]

        # test loaded flow
        flow = await aload_chain_flow(chain)
        assert flow == fixture["each"]


@pytest.mark.django_db
class TestFlow:
    """Test loading, initializing, and invoking flows:
    sequences, maps, branches, joins, and various permutations of these.
    """

    async def test_sequence(self, lcel_sequence, aix_context):
        fixture = lcel_sequence
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {"input": "test", "sequence_0": 0, "sequence_1": 1}

    async def test_map(self, lcel_map, aix_context):
        """Test a map from the start of a chain"""
        fixture = lcel_map
        chain = fixture["chain"]

        # assert flow
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {
            "a": {"input": "test", "node1": 0},
            "b": {"input": "test", "node2": 0},
        }

    async def test_map_with_one_branch(self, lcel_map_with_one_branch, aix_context):
        fixture = lcel_map_with_one_branch
        chain = fixture["chain"]

        # assert flow
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {
            "a": {"input": "test", "node1": 0},
        }

    async def test_sequence_in_map_start(self, lcel_sequence_in_map_start, aix_context):
        """Test a map with a nested sequence. First node in chain is the map."""
        fixture = lcel_sequence_in_map_start
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {
            "a": {"input": "test", "node1": 0},
            "b": {"input": "test", "sequence_0": 0, "sequence_1": 1},
            "c": {"input": "test", "node2": 0},
        }

    async def test_sequence_in_map_in_sequence(
        self, lcel_sequence_in_map_in_sequence, aix_context
    ):
        """Test a map containing a sequence, that is contained in a sequence.

        Tests that sequence_in_map works when the map is not the first node in the chain.
        """
        fixture = lcel_sequence_in_map_in_sequence
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {
            "a": {"input": "test", "node1": 0, "node2": 0},
            "b": {"input": "test", "node1": 0, "sequence_0": 0, "sequence_1": 1},
            "c": {"input": "test", "node1": 0, "node3": 0},
            "node4": 0,
        }

    async def test_sequence_in_map_in_sequence_n2(
        self, lcel_sequence_in_map_in_sequence_n2, aix_context
    ):
        """Test a map containing a sequence, that is contained in a sequence.

        Tests that sequence_in_map works when the map is not the first node in the chain.
        """
        fixture = lcel_sequence_in_map_in_sequence_n2
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {
            "a": {"input": "test", "node1": 0, "node2": 0},
            "b": {"input": "test", "node1": 0, "sequence_0": 0, "sequence_1": 1},
            "c": {"input": "test", "node1": 0, "node3": 0},
            "node4": 0,
            "node5": 0,
        }

    async def test_map_in_sequence_start(self, lcel_map_in_sequence_start, aix_context):
        """Test a sequence starting with a map. First node in chain is a map"""
        fixture = lcel_map_in_sequence_start
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {
            "a": {"input": "test", "a": 0},
            "b": {"input": "test", "b": 0},
            "c": {"input": "test", "c": 0},
            "node2": 0,
        }

    async def test_map_in_sequence_start_n2(
        self, lcel_map_in_sequence_start_n2, aix_context
    ):
        """Test a sequence starting with a map. First node in chain is a map"""
        fixture = lcel_map_in_sequence_start_n2
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {
            "a": {"input": "test", "a": 0},
            "b": {"input": "test", "b": 0},
            "c": {"input": "test", "c": 0},
            "node2": 0,
            "node3": 0,
        }

    async def test_map_in_sequence(self, lcel_map_in_sequence, aix_context):
        """Test a sequence with a nested map. First node in chain is the first node of sequence."""
        fixture = lcel_map_in_sequence
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {
            "a": {"input": "test", "node1": 0, "a": 0},
            "b": {"input": "test", "node1": 0, "b": 0},
            "c": {"input": "test", "node1": 0, "c": 0},
            "node2": 0,
        }

    async def test_map_in_sequence_n2(self, lcel_map_in_sequence_n2, aix_context):
        """Test a sequence with a nested map. First node in chain is the first node of sequence."""
        fixture = lcel_map_in_sequence_n2
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {
            "a": {"input": "test", "node1": 0, "a": 0},
            "b": {"input": "test", "node1": 0, "b": 0},
            "c": {"input": "test", "node1": 0, "c": 0},
            "node2": 0,
            "node3": 0,
        }

    async def test_map_in_map(self, lcel_map_in_map, aix_context):
        """Test a map with a nested map"""
        fixture = lcel_map_in_map
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {
            "a": {"input": "test", "node1": 0},
            "b": {
                "a": {"input": "test", "a": 0},
                "b": {"input": "test", "b": 0},
                "c": {"input": "test", "c": 0},
            },
            "c": {"input": "test", "node2": 0},
        }

    async def test_map_in_map_in_sequence_start(
        self, lcel_map_in_map_in_sequence_start, aix_context
    ):
        """Test a map with a nested map"""
        fixture = lcel_map_in_map_in_sequence_start
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {
            "a": {"input": "test", "node1": 0},
            "b": {
                "a": {"input": "test", "a": 0},
                "b": {"input": "test", "b": 0},
                "c": {"input": "test", "c": 0},
            },
            "c": {"input": "test", "node2": 0},
            "node3": 0,
        }

    async def test_map_in_map_in_sequence_start_n2(
        self, lcel_map_in_map_in_sequence_start_n2, aix_context
    ):
        """Test a map with a nested map"""
        fixture = lcel_map_in_map_in_sequence_start_n2
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {
            "a": {"input": "test", "node1": 0},
            "b": {
                "a": {"input": "test", "a": 0},
                "b": {"input": "test", "b": 0},
                "c": {"input": "test", "c": 0},
            },
            "c": {"input": "test", "node2": 0},
            "node3": 0,
            "node4": 0,
        }

    async def test_map_in_map_in_sequence(
        self, lcel_map_in_map_in_sequence, aix_context
    ):
        """Test a map with a nested map"""
        fixture = lcel_map_in_map_in_sequence
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {
            "a": {"input": "test", "node1": 0, "node2": 0},
            "b": {
                "a": {"input": "test", "node1": 0, "a": 0},
                "b": {"input": "test", "node1": 0, "b": 0},
                "c": {"input": "test", "node1": 0, "c": 0},
            },
            "c": {"input": "test", "node1": 0, "node3": 0},
        }

    async def test_map_in_map_in_sequence_n2(
        self, lcel_map_in_map_in_sequence_n2, aix_context
    ):
        """Test a map with a nested map"""
        fixture = lcel_map_in_map_in_sequence_n2
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {
            "a": {"input": "test", "node1": 0, "node2": 0},
            "b": {
                "a": {"input": "test", "node1": 0, "a": 0},
                "b": {"input": "test", "node1": 0, "b": 0},
                "c": {"input": "test", "node1": 0, "c": 0},
            },
            "c": {"input": "test", "node1": 0, "node3": 0},
            "node4": 0,
            "node5": 0,
        }

    async def test_branch(self, lcel_branch, aix_context):
        fixture = lcel_branch
        chain = fixture["chain"]

        # test loaded flow (default branch)
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})

        # default branch
        assert output == {"input": "test", "node1": 0}

        # named branches
        assert await flow.ainvoke(input={"a": 1}) == {"a": 1, "node2": 0}
        assert await flow.ainvoke(input={"b": 1}) == {"b": 1, "node3": 0}

        # test branch ordering, first branch (a) will execute when both are present
        assert await flow.ainvoke(input={"a": 1, "b": 1}) == {
            "a": 1,
            "b": 1,
            "node2": 0,
        }

        # test that falsy key will not trigger branch
        assert await flow.ainvoke(input={"a": 0, "b": 0}) == {
            "a": 0,
            "b": 0,
            "node1": 0,
        }

    async def test_branch_in_branch(self, lcel_branch_in_branch, aix_context):
        """Test a branch with a nested branch"""
        fixture = lcel_branch_in_branch
        chain = fixture["chain"]

        # test loaded flow
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {"input": "test", "node5": 0}

    async def test_branch_in_default_branch(
        self, lcel_branch_in_default_branch, aix_context
    ):
        """Test a branch with a nested branch"""
        fixture = lcel_branch_in_default_branch
        chain = fixture["chain"]

        # test loaded flow
        flow = await ainit_chain_flow(chain, context=aix_context)

        # default branches
        assert await flow.ainvoke(input={"input": "test"}) == {
            "input": "test",
            "inner_default": 0,
        }
        assert await flow.ainvoke(input={"inner_a_in": 1}) == {
            "inner_a_in": 1,
            "inner_a": 0,
        }
        assert await flow.ainvoke(input={"inner_b_in": 1}) == {
            "inner_b_in": 1,
            "inner_b": 0,
        }

        # non-default branch (inner_a params have no effect)
        assert await flow.ainvoke(input={"a_in": 1, "inner_a_in": 1}) == {
            "a_in": 1,
            "inner_a_in": 1,
            "a": 0,
        }
        assert await flow.ainvoke(input={"b_in": 1, "inner_a_in": 1}) == {
            "b_in": 1,
            "inner_a_in": 1,
            "b": 0,
        }

    async def test_sequence_in_branch(self, lcel_sequence_in_branch, aix_context):
        """Test a branch with a nested sequence"""
        fixture = lcel_sequence_in_branch
        chain = fixture["chain"]

        # test loaded flow
        flow = await ainit_chain_flow(chain, context=aix_context)
        assert await flow.ainvoke(input={"input": "test"}) == {
            "input": "test",
            "default": 0,
        }
        assert await flow.ainvoke(input={"a": 1}) == {
            "a": 1,
            "sequence_0": 0,
            "sequence_1": 1,
        }
        assert await flow.ainvoke(input={"b": 1}) == {"b": 1, "node1": 0}

    async def test_sequence_in_default_branch(
        self, lcel_sequence_in_default_branch, aix_context
    ):
        """Test a branch with a nested sequence"""
        fixture = lcel_sequence_in_default_branch
        chain = fixture["chain"]

        # sanity check setup
        assert isinstance(fixture["branch"], BranchPlaceholder)
        assert fixture["branch"].default == fixture["inner_sequence"]

        # test loaded flow
        flow = await ainit_chain_flow(chain, context=aix_context)
        assert await flow.ainvoke(input={"input": "test"}) == {
            "input": "test",
            "sequence_0": 0,
            "sequence_1": 1,
        }
        assert await flow.ainvoke(input={"a": 1}) == {"a": 0}
        assert await flow.ainvoke(input={"b": 1}) == {"b": 0}

    async def test_map_in_branch(self, lcel_map_in_branch, aix_context):
        """Test a branch with a nested map"""
        fixture = lcel_map_in_branch
        chain = fixture["chain"]

        # test loaded flow
        flow = await ainit_chain_flow(chain, context=aix_context)
        assert await flow.ainvoke(input={"input": "test"}) == {
            "input": "test",
            "default": 0,
        }
        assert await flow.ainvoke(input={"a": 1}) == {"a": 1, "node1": 0}
        assert await flow.ainvoke(input={"b": 1}) == {
            "a": {"b": 1, "a": 0},
            "b": {"b": 0},
            "c": {"b": 1, "c": 0},
        }

    async def test_map_in_default_branch(self, lcel_map_in_default_branch, aix_context):
        """Test a branch with a nested map"""
        fixture = lcel_map_in_default_branch
        chain = fixture["chain"]

        # test loaded flow
        flow = await ainit_chain_flow(chain, context=aix_context)
        assert await flow.ainvoke(input={"input": "test"}) == {
            "a": {"input": "test", "a": 0},
            "b": {"input": "test", "b": 0},
            "c": {"input": "test", "c": 0},
        }
        assert await flow.ainvoke(input={"a": 1}) == {"a": 0}
        assert await flow.ainvoke(input={"b": 1}) == {"b": 0}

    async def test_branch_in_sequence(self, lcel_branch_in_sequence, aix_context):
        fixture = lcel_branch_in_sequence
        chain = fixture["chain"]

        # test loaded flow
        flow = await ainit_chain_flow(chain, context=aix_context)
        assert await flow.ainvoke(input={"input": "test"}) == {
            "input": "test",
            "node0": 0,
            "node1": 0,
            "node4": 0,
            "node5": 0,
        }
        assert await flow.ainvoke(input={"a": 1}) == {
            "a": 1,
            "node0": 0,
            "node2": 0,
            "node4": 0,
            "node5": 0,
        }
        assert await flow.ainvoke(input={"b": 1}) == {
            "b": 1,
            "node0": 0,
            "node3": 0,
            "node4": 0,
            "node5": 0,
        }

    @pytest.mark.skip(reason="not supported yet")
    async def test_branch_in_map_in_sequence(
        self, lcel_branch_in_map_in_sequence, aix_context
    ):
        fixture = lcel_branch_in_map_in_sequence
        chain = fixture["chain"]

        # test loaded flow
        flow = await aload_chain_flow(chain)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {}

    @pytest.mark.skip(reason="not supported yet")
    async def test_branch_in_map_start(self, lcel_branch_in_map_start, aix_context):
        fixture = lcel_branch_in_map_start
        chain = fixture["chain"]

        # test loaded flow
        flow = await ainit_chain_flow(chain, context=aix_context)
        output = await flow.ainvoke(input={"input": "test"})
        assert output == {}

    async def test_join_after_branch(self, lcel_join_after_branch, aix_context):
        """Test a join after a branch

        The join is two sequences that link to the same node/placeholder/component
        instance. This way when instantiated the chain only has one instance of
        the component.

                  |--> *: [node1]---|
        [branch]--+                 |
                  |--> a: [node2] --|
                  +                 +--> [node4] --> [node5]
                  |--> b: [node3] --|

        This is structured as separate sequences for both `a` and `b`, but `node4`
        and `node5` are the same component instance.

                  |--> *: [node1] --> [node4] --> [node5]
        [branch]--+
                  |--> a: [node2] --> [node4] --> [node5]
                  +
                  |--> b: [node3] --> [node4] --> [node5]
        """
        fixture = lcel_join_after_branch
        chain = fixture["chain"]

        # test loaded flow
        flow = await ainit_chain_flow(chain, context=aix_context)

        # default
        assert await flow.ainvoke(input={"input": "test"}) == {
            "input": "test",
            "node1": 0,
            "node4": 0,
            "node5": 0,
        }
        assert await flow.ainvoke(input={"a": 1}) == {
            "a": 1,
            "node2": 0,
            "node4": 0,
            "node5": 0,
        }
        assert await flow.ainvoke(input={"b": 1}) == {
            "b": 1,
            "node3": 0,
            "node4": 0,
            "node5": 0,
        }

    async def test_each(self, lcel_flow_each, aix_context: IxContext):
        """
        Test invoking a RunnableEach
        :param lcel_flow_each:
        :param aix_context:
        :return:
        """
        fixture = lcel_flow_each
        chain = fixture["chain"]
        runnable = await ainit_chain_flow(chain, context=aix_context)

        # validate loaded instance
        assert isinstance(runnable, IxNode)
        assert isinstance(runnable.child, RunnableEach)
        assert isinstance(runnable.child.bound, IxNode)
        assert isinstance(runnable.child.bound.child, MockRunnable)

        # validate output
        result = await runnable.ainvoke(input=["value1", "value2", "value3"])
        assert result == [
            {"input": "value1", "node1": 0},
            {"input": "value2", "node1": 0},
            {"input": "value3", "node1": 0},
        ]

    async def test_sequence_in_each(
        self, lcel_flow_each_sequence, aix_context: IxContext
    ):
        """Sequence in the RunnableEach's workflow"""
        fixture = lcel_flow_each_sequence
        chain = fixture["chain"]
        runnable = await ainit_chain_flow(chain, context=aix_context)

        # validate loaded instance
        assert isinstance(runnable, IxNode)
        runnable_each = runnable.child
        assert isinstance(runnable_each, RunnableEach)
        assert isinstance(runnable_each.bound, RunnableSequence)

        # validate output
        result = await runnable.ainvoke(input=["value1", "value2", "value3"])
        assert result == [
            {"input": "value1", "node1": 0, "node2": 0},
            {"input": "value2", "node1": 0, "node2": 0},
            {"input": "value3", "node1": 0, "node2": 0},
        ]

    async def test_each_in_sequence(
        self, lcel_flow_each_in_sequence, aix_context: IxContext
    ):
        """A RunnableEach in sequence with other nodes."""
        fixture = lcel_flow_each_in_sequence
        chain = fixture["chain"]
        runnable = await ainit_chain_flow(chain, context=aix_context)

        # validate loaded instance
        assert isinstance(runnable, RunnableSequence)
        runnable_each = runnable.first
        assert isinstance(runnable_each.child, RunnableEach)
        assert isinstance(runnable_each.child.bound, IxNode)
        assert isinstance(runnable_each.child.bound.child, MockRunnable)

        # validate output
        result = await runnable.ainvoke(input=["value1", "value2", "value3"])
        assert result == {
            "input": [
                {"input": "value1", "node1": 0},
                {"input": "value2", "node1": 0},
                {"input": "value3", "node1": 0},
            ],
            "node2": 0,
        }


@pytest.mark.django_db
class TestExampleFlows:
    """
    Tests for example flows that may be tricky. Generally something that was
    tested in TestLoadFlow and TestFlow but didnt work in the UX created flow.
    """

    async def test_pirate_flow(self, anode_types, aix_context, mock_openai):
        """Test a flow with a pirate component"""

        await aload_fixture("agent/pirate")
        chain = await Chain.objects.aget(agent__alias="pirate")

        # init flow
        runnable = await ainit_chain_flow(chain, context=aix_context)

        # TODO: Disabling for now. need to mock redis memory because
        #  it's returning empty. Was tested manually with @pirate
        # verify context map works as expected
        # gather_context = runnable.first
        # context = await gather_context.ainvoke(input={"user_input": "test"})
        # assert context == {
        #    "user_input": "test",
        #    "memories": {"chat_history": "mock memory"},
        # }

        output = await runnable.ainvoke(input={"user_input": "test"})
        assert output == {
            "user_input": "test",
            "chat_output": AIMessage(content="mock llm response"),
        }

    @pytest.mark.skip(reason="mocks for streaming not working")
    async def test_each(self, anode_types, aix_context):
        await aload_fixture("agent/each")
        chain = await Chain.objects.aget(agent__alias="each")

        # init flow
        runnable = await chain.aload_chain(context=aix_context)
        output = await runnable.ainvoke(input={"user_input": "test"})
        assert output == [
            {
                "content": "Graceful feline leaps,\nWhiskers twitch, eyes gleam with pride,\nCats, nature's delight.",
                "additional_kwargs": {},
                "type": "AIMessageChunk",
                "example": False,
            },
            {
                "content": "Vast expanse above,\nStars and planets dance in space,\nMysteries unfold.",
                "additional_kwargs": {},
                "type": "AIMessageChunk",
                "example": False,
            },
        ]
