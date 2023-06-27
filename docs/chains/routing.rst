Flow Control Chains
===================

Flow Control Chains are a group of Chain subclasses in the ``ix.chains.routing`` module that
handle flow control tasks. Flow control chains are designed to handle complex operations such
as mapping and reducing data, iterating over lists, and so on. Each of these operations is
encapsulated in a different chain subclass.


ChooseTool
-----------

ChooseTool is a subclass of Chain that selects a subchain that can best respond to ``user_input``. Each subchain
requires a name and description. ChooseTool prompts the LLM to decide based on a comparison of ``user_input``
and the subchain descriptions.


Example
^^^^^^^

.. code-block:: python

    from ix.chains.tool_chooser import ChooseTool
    from ix.chains.management.commands.create_dad_jokes_v1 import DAD_JOKESTER
    from ix.chains.management.commands.create_fake_weather_v1 import FAKE_WEATHERMAN

    CHOOSE_TOOL_CONFIG = {
        "class_path": "ix.chains.tool_chooser.ChooseTool",
        "node_type": "map",
        "config": {
            "llm": {
                "class_path": "langchain.chat_models.openai.ChatOpenAI",
            },
            chains: [
                DAD_JOKESTER
                FAKE_WEATHERMAN
            ]
        }
    }

    chain = Chain.objects.create(
        name="Example ToolChooser",
        description="Chooses from subchains based on user input",
    )

    # create nodes, including two subchains
    ChainNode.objects.create_from_config(chain, CHOOSE_TOOL_CONFIG, root=True)



MapSubchain
-----------


MapSubchain is a subclass of Chain that runs a subchain for each element in a list input.

.. note:: The input list is read from inputs using jsonpath set as ``map_input`` and mapped as input_variable ``map_input_to``. ``map_input_to`` is automatically added to input_variables if not already present. Each iteration will receive the outputs of the previous iteration under the key ``outputs``. Results are output as a list under ``output_key``.

Class Attributes
^^^^^^^^^^^^^^^^^^^

- ``chain``: Instance of Chain
- ``input_variables``: List of input variable names as strings
- ``map_input``: String name of the map input
- ``map_input_to``: String name of the variable to map input to
- ``output_key``: String key for the output list


Creating a MapSubchain
^^^^^^^^^^^^^^^^^^^^^^

This class method loads a MapSubchain instance from a configuration dictionary.

.. code-block:: python

    from ix.chains.routing import MapSubchain
    from ix.chains.tests.mock_chain import MOCK_CHAIN_CONFIG

    EXAMPLE_CONFIG = {
        'input_variables': ['input1'],
        'map_input': 'input1',
        'map_input_to': 'mock_chain_input',
        'output_key': 'output1'
        'chains': [MOCK_CHAIN_CONFIG],
    }

    # create nodes
    chain = Chain.objects.create(
        pk=CHAIN_ID,
        name="Greeting chain",
        description="Chain used to greet the user",
    )
    node = ChainNode.objects.create_from_config(chain, EXAMPLE_CONFIG, root=True)

    # load chain
    langchain_chain = chain.load(mock_callback_manager)

    # run chain
    inputs = {"input1": ["test1", "test2", "test3"]}
    output = langchain_chain.run(**inputs)
    assert output == ["test1", "test2", "test3"]

Selecting input with ``map_input``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``map_input`` attribute uses a jsonpath expression to extract
the required data from the input. This can either refer to a
specific key directly or follow a path through the input structure
to a key.

Jsonpath is a query language for JSON, similar to XPath for XML.
It provides a simple way to extract specific data points from a
complex JSON structure. In the context of the ``MapSubchain``,
the jsonpath expression set in ``map_input`` is used to navigate
through the input and find the data that needs to be passed to
the subchain.

For example, if our input is a nested structure and we need to map
the ``input1`` list located within the ``nested`` dictionary, we would
set ``map_input`` to ``$.nested.input1``.

.. code-block:: python

    inputs = {
        "nested": {
            "input1": ["test1", "test2", "test3"]
        }
    }

    output = map_subchain.run(**inputs)
    assert output == ["test1", "test2", "test3"]


You can also use the NodeChain to create an instance of MapSubchain:
