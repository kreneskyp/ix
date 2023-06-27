Chain Memory
############

Chains support Langchain memory classes. To add memory to a chain, add a ``memory`` field to the ``config`` of the
chain.


Details on available memory classes:

* `Langchain memory classes <https://python.langchain.com/en/latest/modules/memory/how_to_guides.html>`_
* `Artifact Memory <docs/chains/artifacts.rst>`_


Usage
=====

Basic Example:
--------------

.. code-block:: python

    # Defining memory class with llm and backend config
    SUMMARY_MEMORY = {
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
                "config": {"url": "redis://redis:6379/0"},
            },
        },
    }

    # Prompt contains {chat_summary} input variable to hold the conversation summary
    # The variable is set by `memory_key` in the memory config
    PIRATE_PROMPT = """
    You are a pirate. Talk like a pirate in all responses.

    CHAT_SUMMARY:
    {chat_summary}
    """

    # The chain must include input_variables required for the memory class.
    # In this example, the message templates define the input_variables for
    # the chains.
    CHAT_MESSAGES_WITH_HISTORY: [
        {
            "role": "system",
            "template": PIRATE_PROMPT,
            "input_variables": ["chat_summary"],
        },
        {
            "role": "user",
            "template": "{user_input}",
            "input_variables": ["user_input"],
        },
    ],

    # Chain config with memory
    PIRATE = {
        "class_path": "ix.chains.llm_chain.LLMReply",
        "config": {
            "llm": {
                "class_path": "langchain.chat_models.openai.ChatOpenAI",
            },
            "memory": SUMMARY_MEMORY,
            "messages": CHAT_MESSAGES_WITH_HISTORY,
        },
    }

     # Create root node as a sequence
    root = ChainNode.objects.create(**PIRATE)


Multiple Memory Classes
------------------------

Multiple memory classes may be used in a chain. The ``memory`` field accepts a single config object or a list of
objects. The memory classes will automatically be combined with a LangChain ``CombinedMemory`` class.

.. code-block:: python

    ARTIFACT_MEMORY = {
        "class_path": "ix.memory.artifacts.ArtifactMemory",
    }

    PIRATE_WITH_ARTIFACTS = {
        "class_path": "ix.chains.llm_chain.LLMReply",
        "config": {
            "llm": {
                "class_path": "langchain.chat_models.openai.ChatOpenAI",
            },
        "memory":[SUMMARY_MEMORY, ARTIFACT_MEMORY]
    }


Configuring Sessions
---------------------

Memory session may be scoped to ``chat``, ``agent``, ``task``, ``user``.

The chain loader builds a ``session_id`` based on the scope and the runtime context. The identifier for the scope
is included in the ``session_id``. For ``chat.id`` is included for ``chat`` scope.

Sessions may be added to the memory class or the backend depending on the implementation. For example
``langchain.memory.BaseChatMessageHistory`` backends handle sessions for ``langchain.memory.BaseChatMemory``.

Example session config:

.. code-block:: python

    # memory with this config will be scoped to the agent
    # and use session_id `agent_<agent.id>`
    AGENT_SESSION_CONFIG = {
        "url": "redis://redis:6379/0"
        "session_scope": "agent"
    }

    AGENT_SCOPED_SUMMARY_MEMORY = {
        "class_path": "langchain.memory.ConversationBufferMemory",
        "config": {
            "input_key": "user_input",
            "memory_key": "chat_summary",
            "max_token_limit": 1500,
            "backend": {
                "class_path": "langchain.memory.RedisChatMessageHistory",
                "config": {

                    "session": AGENT_SESSION_CONFIG
                },
            },
        },
    }



A prefix may be added to the ``session_id`` by adding a ``prefix`` field to the session config. The prefix allows
for memory to be partitioned within the scope. For example, a subset of agents or chains in the chat may share
a memory partition.

.. code-block:: python

    # memory with this config will be scoped to the chat and the prefix
    # the session id will be `group_1_chat_<chat.id>`
    PREFIXED_AGENT_SESSION_CONFIG = {
        "url": "redis://redis:6379/0"
        "session_scope": "chat",
        "session_prefix": "group_1"
    }


Memory Backends
----------------

Memory classes such as ``ConversationBufferMemory`` and ``ConversationSummaryBufferMemory`` require a backend to store
the conversation history. The backend is configured by adding a ``chat_memory`` field to the memory config.

.. code-block:: python

    REDIS_MEMORY_BACKEND = {
        "class_path": "langchain.memory.RedisChatMessageHistory",
        "config": "PREFIXED_AGENT_SESSION_CONFIG"
    },


Memory LLMs
------------

Memory classes such as ``ConversationSummaryMemory`` and ``ConversationSummaryBufferMemory`` require an LLM to generate
summarizations of the conversation history. The LLM is configured by adding a ``llm`` field to the memory config.

.. code-block:: python

    MEMORY_LLM = {
        "class_path": "langchain.chat_models.openai.ChatOpenAI",
        "config": {
            "verbose": True,
        },
    },
