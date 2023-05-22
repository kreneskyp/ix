Data Processing Chains
======================

Data processing chains manipulate data or inputs in some way.


ParseJSON
-----------

ParseJSON takes an input string and parses it as JSON. It is useful for
processing LLM responses into JSON.

Input and output keys may be mapped with ``input_key`` and ``output_key`` respectively.

Example
^^^^^^^

.. code-block:: python

    PARSE_JSON_CONFIG = {
        "class_path": "ix.chains.json.ParseJSON",
        "config" : {
            "input_key": "llm_response",
            "output_key": "llm_response_json",
        }
    }

    # create node
    root = ChainNode.objects.create(**PARSE_JSON_CONFIG)
