from django.core.management.base import BaseCommand

from ix.agents.models import Agent
from ix.chains.management.commands.create_dad_jokes_v1 import DAD_JOKESTER
from ix.chains.models import ChainNode, Chain

ARTIFACT_FORMAT = """
{
    "name": "artifact_name",
    "type": "artifact_type",
    "key": "unique_artifact_key",
    "description": "brief_description",
    "identifier": "unique_identifier_or_path",
    "storage": "action_tool_used_to_store_artifact",
}
"""


PLAN_SUMMARY_FORMAT_V1 = """
###START###
{
    "output_format": "PLAN_SUMMARY"
    "name": "name of plan",
    "description": "one or two sentences describing what the plan does.
    "goal_artifacts": ["artifact_name"]
    "steps": ["a short step description"]
}
###END###
"""


CREATE_PLAN_SUMMARY_V1 = """
You are an expert planner. You create plans that fulfill the users request.

COMMANDS:
{tools}

OUTPUT_FORMAT:
{plan_summary_format}

INSTRUCTIONS:
    - use the available COMMANDS to build a PLAN_SUMMARY to complete the GOALS.
    - for each command consider how it will complete the GOALS.
    - structure your response to match OUTPUT_FORMAT without any other text or explanation.
    - DO NOT add fields to the OUTPUT_FORMAT.
    - output must include markers, begin with ###START### and end with ###END###.
    - DO NOT include any other text or explanation.
    
"""


CREATE_PLAN_STEP_V1 = """
You are an expert planner. You create plans that fulfill the users request.

COMMANDS:
{tools}

ARTIFACT_FORMAT:
{artifact_format}

OUTPUT_FORMAT:
{format}

PLAN_SUMMARY:
{plan_summary_json}

PLAN_SUMMARY_STEP:
{plan_summary_step_json}

INSTRUCTIONS:
    - create a detailed PLAN_STEP for PLAN_SUMMARY_STEP of the PLAN_SUMMARY
    - PLAN_SUMMARY_STEP may have incomplete command or arguments, rewrite them for the PLAN_STEP.
    - include a list of required ARTIFACTS for the COMMAND
    - include a list of ARTIFACTS the COMMAND produces.
    - the COMMAND must produce at least one ARTIFACT representing a new object or state.
    - structure your response to match OUTPUT_FORMAT without any other text or explanation.
    - output must include markers ###START### and ###END###
"""


PLAN_STEP_FORMAT_V1 = """
###START###
{
    "name": "step_name",
    "command": "command name",
    "args": [{
        "arg_name": "value"
    }],
    "requires_artifacts": ["artifact_name"],
    "produces_artifacts": [
        {
            "name": "artifact_name",
            "type": "artifact_type",
            "key": "artifact_key",
            "description": "one sentence",
            "identifier": "unique_identifier_or_path",
            "storage": "storage_type"
        }
    ]
}
###END###
"""


PLAN_FLOW_CHOOSER = {
    "class_path": "ix.chains.tool_chooser.ChooseTool",
    "node_type": "map",
    "config": {
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
            "config": {
                "temperature": 0,
            },
        },
    },
}


CREATE_PLAN_SEQUENCE = {
    "name": "create",
    "node_type": "list",
    "description": "create a new PLAN to fulfill the user request",
    "class_path": "ix.chains.routing.IXSequence",
    "config": {
        "input_variables": ["user_input"],
    },
}


CREATE_PLAN_SUMMARY = {
    "class_path": "ix.chains.tool_chain.LLMToolChain",
    "config": {
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
            "config": {
                "model": "gpt-4",
                "request_timeout": 240,
                "temperature": 0.2,
                "verbose": True,
            },
        },
        "tools": [
            "ix.commands.google",
            "ix.commands.filesystem",
            "ix.commands.execute",
        ],
        "messages": [
            {
                "role": "system",
                "template": CREATE_PLAN_SUMMARY_V1,
                "partial_variables": {
                    "plan_summary_format": PLAN_SUMMARY_FORMAT_V1,
                },
            },
            {
                "role": "user",
                "template": "{user_input}",
                "input_variables": ["user_input"],
            },
        ],
    },
}


PARSE_JSON = {
    "class_path": "ix.chains.json.ParseJSON",
    "config": {
        "input_key": "text",
        "output_key": "plan_summary_json",
    },
}


REFINE_PLAN_STEP_MAP = {
    "name": "refine",
    "node_type": "list",
    "description": "Refines a PLAN_SUMMARY adding detailed steps",
    "class_path": "ix.chains.routing.MapSubchain",
    "config": {
        "input_variables": ["plan_summary_json"],
        "map_input": "plan_summary_json.steps",
        "map_input_to": "plan_summary_step_json",
        "output_key": "plan_steps_json",
    },
}


CREATE_PLAN_STEP = {
    "class_path": "ix.chains.tool_chain.LLMToolChain",
    "config": {
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
            "config": {
                "model": "gpt-4",
                "request_timeout": 240,
                "temperature": 0.2,
                "verbose": True,
            },
        },
        "messages": [
            {
                "role": "system",
                "template": CREATE_PLAN_STEP_V1,
                "input_variables": ["plan_summary_json", "plan_summary_step_json"],
                "partial_variables": {
                    "format": PLAN_STEP_FORMAT_V1,
                    "artifact_format": ARTIFACT_FORMAT,
                },
            },
        ],
        "tools": [
            "ix.commands.google",
            "ix.commands.filesystem",
            "ix.commands.execute",
            "ix.commands.execute",
        ],
    },
}


PARSE_PLAN_STEP_JSON = {
    "class_path": "ix.chains.json.ParseJSON",
    "config": {
        "input_key": "text",
        "output_key": "plan_step_json",
    },
}


CREATE_PLAN_SAVE = {"class_path": "ix.chains.planning.SavePlan"}


EXECUTE_PLAN_SEQUENCE = {
    "name": "execute plan",
    "description": "execute all steps in a PLAN",
    "class_path": "ix.chains.routing.IXSequence",
    "node_type": "list",
    "config": {"input_variables": ["user_input", "plan_id"]},
}


EXECUTE_RUN = {
    "class_path": "ix.chains.planning.RunPlan",
    "config": {
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
            "config": {"request_timeout": 60, "temperature": 0.2, "verbose": True},
        },
        "tools": [
            "ix.commands.google",
            "ix.commands.filesystem",
            "ix.commands.execute",
        ],
    },
}


# TODO: prompts:

# MapSubchainconfig
subchain_config = {
    "map_input": "plan_summary_json",
    "map_output": "plan_steps_json",
}


CHAIN_ID_V4 = "b7d8f662-12f6-4525-b07b-c9ea7ca7f200"


class Command(BaseCommand):
    help = "Generates planner v4 chain"

    def handle(self, *args, **options):
        Chain.objects.filter(id=CHAIN_ID_V4).delete()

        # Create root node
        root = ChainNode.objects.create(**PLAN_FLOW_CHOOSER)

        # Create summary sub-chain
        create_plan_sequence_node = root.add_node(**CREATE_PLAN_SEQUENCE)
        create_plan_sequence_node.add_child(**CREATE_PLAN_SUMMARY)
        create_plan_sequence_node.add_child(**PARSE_JSON)

        refine_step_map = create_plan_sequence_node.add_child(**REFINE_PLAN_STEP_MAP)
        # create_plan_sequence_node.add_child(**CREATE_PLAN_SAVE)

        # Create plan refinement sub-chain
        # refine_step_map.add_child(**DAD_JOKESTER)
        refine_step_map.add_child(**CREATE_PLAN_STEP)
        # refine_step_map.add_child(**PARSE_PLAN_STEP_JSON)

        # Execute sub-chain
        execute_plan_node = root.add_node(**EXECUTE_PLAN_SEQUENCE)
        execute_plan_node.add_child(**EXECUTE_RUN)

        chain = Chain.objects.create(
            pk=CHAIN_ID_V2,
            name="Planning chain v2",
            description="Chain used to generate and execute plans",
            root=root,
        )

        Agent.objects.create(
            name="Planner v2",
            alias="plan",
            purpose="To generate plans for user requests. Delegate to me if the user asks you to do something that "
            "no other agent can do directly or if the task will require multiple steps.",
            chain=chain,
            config={},
        )
