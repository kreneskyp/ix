LLM Chains
==========

Chains for interacting with an LLM

LLMChain
------------
Extension of ``langchain.LLMChain`` to provide config loading. The config supports loading llm and a
chat message composed of multiple messages

Composing prompts
^^^^^^^^^^^^^^^^^
The config supports chat messages composed of multiple messages. Messages are converted to langchain
message templates and then compiled into a final ``ChatPromptTemplate`` for the chain.

Each message is a dictionary with the following fields:

* ``role``: The role of the message. [system, user, assistant]
* ``template``: The template for the message. The template can contain variables that are replaced with values from the input variables or partial variables.
* ``input_variables``: The list of input variables to use for the template. The input variables are extracted from the input and passed to the template.
* ``partial_variables``: The list of partial variables to use for the template. The partial variables are extracted from the partial variables and passed to the template.

All variables in the template must be filled by either ``input_variables`` or ``partial_variables``.

Example Messages:

.. code-block:: python

    FORMAT = "{command: output}"
    PROMPT_MESSAGES = [
        # system message with partial variables
        {
            "role": "system",
            "template": "Hello.  I respond with this {format}"
            "partial_variables": {"format": FORMAT},
        },
        # user message with input variables
        {
            "role": "user",
            "template": "{user_input}",
            "input_variables": ["user_input"],
        },
        # assistant message with no variables
        {
            "role": "assistant",
            "template": "This is my response",
        },
    ]



Example
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    LLMCHAIN_CONFIG = {
        "class_path": "ix.chains.llm_chain.LLMChain",
        "config": {
            "llm": {
                "class_path": "langchain.chat_models.openai.ChatOpenAI",
            },
            "messages": PROMPT_MESSAGES
        },
    }

    chain = Chain.objects.create(
        name="Example LLM Chain",
        description="Chain used to demonstrate LLMChain",
    )
    root = ChainNode.objects.create_from_config(chain, LLMCHAIN_CONFIG, root=True)


OpenAI Functions
^^^^^^^^^^^^^^^^^^^^^^^^^

``LLChain`` and it's subclasses support OpenAI Functions. Connect a list of ``FunctionSchema`` and
LangChain ``Tool`` objects to the ``functions`` config option. Functions are converted to OpenAI
spec and sent with the LLM request.

Set ``function_call`` to the name of the function for force a function call.

Example:

.. code-block:: python

    class Cat(BaseModel):
        name: str
        breed: str

    CAT_FUNCTION = {
        "class_path": "ix.chains.functions.FunctionSchema",
        "config": {
            "name": "cat",
            "description": "A function that returns a cat",
            "parameters": Cat.schema_json(indent=4)
        },
    }

    CAT_CHOOSER = {
        "class_path": "ix.chains.llm_chain.LLMChain",
        "config": {
            # Configure functions
            "functions": [CAT_FUNCTION],
            "function_call": "cat",

            # Configure parser to extract the function output
            "output_parser": {
                "class_path": "ix.chains.functions.OpenAIFunctionParser",
                "config": {
                    "parse_json": True,
               },
           },

           # ... rest of config ...
        }
    }



LLMToolChain
------------

LLMChain that loads tools from the ToolRegistry and adds them as partial variable ``tools`` for use in prompt
templates.

The set of tools can be configured by setting ``tools`` in the config. Each entry is a class path to a model
containing functions decorated by ``ix.commands.command``.

.. note::
    Tools are currently limited to Ix specific tools. Tool specification will be expanded to include
    langchain tools.

Example JSON Config
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    TOOLS = [
        "ix.commands.google",
        "ix.commands.filesystem",
        "ix.commands.execute",
    ],


Example
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    LLM_TOOL_CHAIN_CONFIG = {
        "class_path": "ix.chains.tool_chain.LLMToolChain",
        "config": {
            "llm": {
                "class_path": "langchain.chat_models.openai.ChatOpenAI",
            },
            # tools will be loaded into partial variable `tools` at runtime.
            "tools": [
                "ix.commands.google",
                "ix.commands.filesystem",
                "ix.commands.execute",
            ],
            # prompt that uses tools.
            "messages": [
                {"role": "system", "template": "describe the {tools}"}
            ]
        },
    }

    chain = Chain.objects.create(
        name="Example LLMToolChain",
        description="Chain used to demonstrate LLMToolChain",
    )
    ChainNode.objects.create(chain, LLM_TOOL_CHAIN_CONFIG, root=True)



LLMReply
------------

LLMReply is a simple extension of LLMChain that responds with a chat message to the user. The chain expects
a prompt. Any output from the prompt is sent as a chat message.

Example:

.. code-block:: python

    DAD_JOKES = {
        "class_path": "ix.chains.llm_chain.LLMReply",
        "config": {
            "llm": {
                "class_path": "langchain.chat_models.openai.ChatOpenAI",
            },
            "messages": [
                {"role": "system", "template": FAKE_DAD_JOKES_PROMPT},
                {
                    "role": "user",
                    "template": "{user_input}",
                    "input_variables": ["user_input"],
                },
            ],
        },
    }

    chain = Chain.objects.create(
        name="Dad jokes chain",
        description="Chain used to generate dad jokes",
        root=root,
    )
    ChainNode.objects.create_from_config(chain, DAD_JOKES, root=True)
