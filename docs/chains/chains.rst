Chains
=================================

This document provides an explanation of the models ``ChainNode`` and ``ChainEdge``, which are used to define a
Langchain processing chain for use in Ix.

Overview
~~~~~~~~

A Langchain processing chain represents a sequence of actions or processes to be applied on a given input. This chain
can involve various types of processes, including interactions with Language Models (LLMs).

In the context of Ix, chains are models using three entities: ``NodeType``, ``ChainNode``, and
``ChainEdge``. These model define the types of components and structure of chains that use them.
Chains are stored in the database and can be loaded into a LangChain instance.

The graph model supports both defining arbitrary processing chains to run them, and also supports displaying and
editing them visually in the user interface. The model supports asynchronicity, including parallel
processing and delegation to other agents.

Chain API Reference
------------
Ix provides custom features on top of LangChain that require custom integrations to load.

Default chain types
^^^^^^^^^^^^^^^^^^^

LLM Chains:

* `LLMChain <./llm.rst#LLMChain>`_: wrapper around ``langchain.LLMChain`` to add Ix runtime.
* `LLMToolChain <./llm.rst#LLMToolChain>`_: chain that has ``tools`` available in the prompt.
* `LLMReply <./llm.rst#LLMReply>`_: Respond to chat stream with the result of an LLM prompt.

Artifacts:

* `SaveArtifact <./artifacts.rst#SaveArtifact>`_: Save an artifact to the chat stream.

Routing / flow control:

* `MapSubchain <./routing.rst#MapSubchain>`_: Run subchain for each item in a list.
* `ChooseTool <./routing.rst#ChooseTool>`_: chain that chooses a tool with a subchain.

Chain options
^^^^^^^^^^^^^^

* `Memory <./memory.rst>`_:  Shared and local scoped memory for chains linked to Ix runtime.
* `OpenAI Functions <./llm.rst#openai-functions>`_: OpenAI API functions for use in chains.


Chain Models
------------

NodeType
^^^^^^^^

A ``NodeType`` defines a LangChain component that may be used in a chain. Both property nodes and chain nodes are
supported. ``NodeType`` instances describe the type of component, configuration options, and how they may be
connected to other nodes.

Note, that all LangChain components require a corresponding ``NodeType``. These definitions are required to provide
support for non-pydantic components including those that use a helper function or wrapper class for loading.
(e.g. Zapier LangChain component requires loading a client).

ChainNode
^^^^^^^^

A ``ChainNode`` represents a single node in the chain. Each node represents a processing step or operation that can be
applied. It stores the configuration necessary for the process, along with additional metadata like its name and
description.

A ``ChainNode`` also maintains references to its parent ``Chain`` allowing the chain to be traversed
and manipulated easily.

ChainEdge
^^^^

A ``ChainEdge`` represents the connection or link between two ``ChainNode`` instances in the chain. It defines the
source and target nodes of the connection, and contains additional information such as the root node of the chain it
belongs to, and an optional input map.

The ``ChainEdge`` model is crucial for defining the structure and flow of the processing chain.

Usage
^^^^

These models are used to dynamically create, modify, and traverse processing chains. Chains stored
in the database may be queried and run.

.. code-block:: python

    # fetch chain, initialize task, and run chain
    chain = Chain.objects.get(pk=CHAIN_ID)
    task = fake_task(chain=chain)
    callback_manager = IxCallbackManager(task)
    langchain_chain = chain.load(callback_manager)
    langchain_chain.run(user_input="Hello, world!")


Creating Chains
^^^^^^^^

Chains may be generated through the visual editor or a python code run as a management command or via shell_plus.
JSON config import is not supported yet.

Here is a simple example of creating a chain that sends a greeting to the user. In this example, a simple chain that
greets the user is created. The chain consists of a single node that uses the hypothetical class ``GreetUserChain`` to
send a greeting message to the user. The ``ChatOpenAI`` language model

.. code-block:: python

    # Define the greeting operation
    GREET_USER = {
        "class_path": "ix.chains.llm.LLMChain",
        "config": {
            "llm": {
                "class_path": "langchain.chat_models.openai.ChatOpenAI",
                "config": {"request_timeout": 60, "temperature": 0.2, "verbose": True},
            },
            "messages": [
                {
                    "role": "system",
                    "template": "Hello, User! How can I assist you today?",
                }
            ],
        },
    }

    # Create the chain
    chain = Chain.objects.create(
        pk=CHAIN_ID,
        name="Greeting chain",
        description="Chain used to greet the user",
    )

    # Create root node
    root = ChainNode.objects.create_from_config(chain, GREET_USER, root=True)



Creating a Sequence
^^^^^^^^^^^^^^^^^^^^

In this next example, a chain with a sequence of actions is created. The chain consists of two nodes: one that uses
the previously defined ``GREET_USER`` and another that asks the user for their name.

The ``ChainEdge`` connecting the nodes is created automatically when adding a child node to an existing node. When
``node_type`` is set to "list", the ``ChainNode`` will automatically create a ``ChainEdge`` with the ``source_node``
set to the parent node and the ``target_node`` set to the newly created child node. The order of the child nodes is
determined by the order in which they are added, and recorded by the ``key`` field of the ``ChainEdge``.


.. code-block:: python

    # Define the operation to ask the user's name
    ASK_USER_NAME = {
        "class_path": "ix.chains.llm.LLMChain",
        "config": {
            "llm": {
                "class_path": "langchain.chat_models.openai.ChatOpenAI",
                "config": {"request_timeout": 60, "temperature": 0.2, "verbose": True},
            },
            "messages": [
                {
                    "role": "system",
                    "template": "What's your name?",
                }
            ],
        },
    }

    SEQUENCE = {
        "class_path": "langchain.chains.SequentialChain",
        "config": {
            "chains": [
                GREET_USER,
                ASK_USER_NAME,
            ]
        }
    }

    # Create the chain
    chain = Chain.objects.create(
        pk=CHAIN_ID,
        name="Greeting and name asking chain",
        description="Chain used to greet the user and ask their name",
    )

    # Create root node as a sequence
    root = ChainNode.objects.create_from_config(chain, SEQUENCE, root=True)

