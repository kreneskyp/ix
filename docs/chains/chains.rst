Chains
=================================

This document provides an explanation of the models ``ChainNode`` and ``ChainEdge``, which are used to define a
Langchain processing chain for use in Ix.

Overview
~~~~~~~~

A Langchain processing chain represents a sequence of actions or processes to be applied on a given input. This chain
can involve various types of processes, including interactions with Language Models (LLMs).

In the context of our Django application, we model this processing chain using two main entities: ``ChainNode`` and
``ChainEdge``. This model is used to define the structure of the chain, and is stored in the database. The actual
processing chain is generated from this model when it is loaded.

The graph model supports both defining arbitrary processing chains to run them, and also supports displaying and
(eventually) editing them visually in the user interface. The model will be extended to support asynchronously
calling other chains and agents.

Chain References
------------
Ix uses a custom loading mechanism and provides custom chain types for flow control. These chains are available
for use by default:

LLM Chains:

* `LLMChain <./llm.rst#LLMChain>`_: wrapper around `langchain.LLMChain` to add config loader.
* `LLMToolChain <./llm.rst#LLMToolChain>`_: chain that has `tools` available in the prompt.
* `LLMReply <./llm.rst#LLMReply>`_: chain that replies to a message with LLM prompt.

Data handling:

* `ParseJSON <./data.rst#ParseJSON>`_: chain that parses a JSON string into a python object.

Routing / flow control:

* `IxSequence <./routing.rst#IxSequence>`_: wrapper for Sequence that provides config loader
* `MapSubchain <./routing.rst#MapSubchain>`_: chain that runs a subchain for each value in a list
* `ChooseTool <./routing.rst#ChooseTool>`_: chain that chooses a tool with a subchain

Chain Models
------------

ChainNode
^^^^^^^^

A ``ChainNode`` represents a single node in the chain. Each node represents a processing step or operation that can be
applied. It stores the configuration necessary for the process, along with additional metadata like its name and
description.

A ``ChainNode`` also maintains references to its parent and root nodes in the chain, allowing the chain to be traversed
and manipulated easily.

A node has a type that defines the way the node interacts with its children in the chain:

- ``node``: A basic node with no specific interaction with its children.
- ``list``: An ordered sequence of children nodes. The order of processing is defined by the order of the children.
- ``map``: A node that maps its children. The order of processing is not predetermined.

ChainEdge
^^^^

A ``ChainEdge`` represents the connection or link between two ``ChainNode`` instances in the chain. It defines the
source and target nodes of the connection, and contains additional information such as the root node of the chain it
belongs to, and an optional input map.

The ``ChainEdge`` model is crucial for defining the structure and flow of the processing chain.

Usage
^^^^

These models are used to dynamically create, modify, and traverse processing chains. You can add nodes to the root or
as a child of an existing node using the ``add_node`` and ``add_child`` methods respectively in the ``ChainNode``
model. The ``load_config`` method is used to load the configuration for a particular node, including its child nodes
if it's of type "list" or "map".

The ``load_chain`` method is used to generate the actual processing chain from the stored models. This method uses
the ``from_config`` class method of the chain class specified by the ``class_path`` field to create the chain.


Creating Chains
^^^^^^^^

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

    # Create root node
    root = ChainNode.objects.create(**GREET_USER)

    # Create the chain
    Chain.objects.create(
        pk=CHAIN_ID,
        name="Greeting chain",
        description="Chain used to greet the user",
        root=root,
    )





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

    # Create root node as a sequence
    root = ChainNode.objects.create(class_path="ix.chains.base.SequenceChain", node_type="list")

    # Add the greeting and name-asking operations to the sequence
    root.add_child(**GREET_USER)
    root.add_child(**ASK_USER_NAME)

    # Create the chain
    Chain.objects.create(
        pk=CHAIN_ID,
        name="Greeting and name asking chain",
        description="Chain used to greet the user and ask their name",
        root=root,
    )

