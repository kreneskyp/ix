from django.core.management.base import BaseCommand

from ix.agents.models import Agent
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

PLAN_FORMAT_V3 = """
###START###
{
    "output_format": "PLAN"
    "name": "name of plan",
    "description": "one or two sentences describing what the plan does.
    "goal_artifacts": [ARTIFACT_FORMAT]
    "commands": [
        {
            name: "step_name",
            "command": {
                "name": "command name",
                "args":{
                    "arg name": "value"
                }
            }
            requires_artifacts: ["artifact_name"]
            produces_artifacts: [ARTIFACT_FORMAT]
        }
    ]
}
###END###
"""


CREATE_PLAN_V3 = """
You are an expert planner. You create plans that fulfill the users request.

COMMANDS:
{tools}

ARTIFACT_FORMAT:
{artifact_format}

OUTPUT_FORMAT:
{format}

ARTIFACTS: Artifacts represent the results or consequences of executing a command or action.
They can be new objects created (e.g., code components, data, files) or changes to the system
or environment state (e.g., modified settings, enabled features, activated services).

INSTRUCTIONS TO CREATE A PLAN:
    - use the available COMMANDS to build a PLAN to complete the GOALS.
    - include a list of required ARTIFACTS for each COMMAND
    - include a list of ARTIFACTS the COMMAND produces.
    - the plan's `goal_artifacts` should fulfill the goal
    - every COMMAND must produce at least one ARTIFACT representing a new object or state.
    - for each command consider how it will complete the GOALS.
    - If you cannot determine a plan or an input, respond using the QUESTION_FORMAT.
    - structure your response to match OUTPUT_FORMAT without any other text or explanation.
    - output must include markers, begin with ###START### and end with ###END### .
"""


PLAN_FLOW_CHOOSER = {
    "class_path": "ix.chains.tool_chooser.ChooseTool",
    "node_type": "map",
    "config": {
        "llm": {
            "class_path": "langchain_community.chat_models.ChatOpenAI",
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


CREATE_PLAN = {
    "class_path": "ix.chains.tool_chain.LLMToolChain",
    "config": {
        "llm": {
            "class_path": "langchain_community.chat_models.ChatOpenAI",
            "config": {
                "model_name": "gpt-4",
                "request_timeout": 600,
                "temperature": 0.1,
                "max_tokens": 5500,
                "verbose": True,
            },
        },
        "messages": [
            {
                "role": "system",
                "template": CREATE_PLAN_V3,
                "partial_variables": {
                    "format": PLAN_FORMAT_V3,
                    "artifact_format": ARTIFACT_FORMAT,
                },
            },
            {
                "role": "user",
                "template": "{user_input}",
                "input_variables": ["user_input"],
            },
        ],
        "tools": [
            "ix.commands.google",
            "ix.commands.filesystem",
            "ix.commands.execute",
        ],
    },
}


CREATE_PLAN_JSON = {
    "class_path": "ix.chains.json.ParseJSON",
    "config": {
        "input_key": "text",
        "output_key": "plan_json",
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
            "class_path": "langchain_community.chat_models.ChatOpenAI",
            "config": {"request_timeout": 60, "temperature": 0.2, "verbose": True},
        },
        "tools": [
            "ix.commands.google",
            "ix.commands.filesystem",
            "ix.commands.execute",
        ],
    },
}


PLANNER_CHAIN_V3 = "b7d8f662-12f6-4525-b07b-c9ea7c10002c"
PLANNER_AGENT_V3 = "b7d8f662-12f6-4525-b07b-c9ea7c10002a"


class Command(BaseCommand):
    help = "Creates planning chain v1"

    def handle(self, *args, **options):
        chain, _ = Chain.objects.get_or_create(
            pk=PLANNER_CHAIN_V3,
            defaults=dict(
                name="Planning chain v3",
                description="Chain used to generate and execute plans.",
            ),
        )

        # Create root node
        root = ChainNode.objects.create(chain=chain, root=True, **PLAN_FLOW_CHOOSER)

        # Create plan sub-chain
        create_plan_sequence_node = root.add_node(**CREATE_PLAN_SEQUENCE)
        create_plan_sequence_node.add_child(**CREATE_PLAN)
        create_plan_sequence_node.add_child(**CREATE_PLAN_JSON)
        create_plan_sequence_node.add_child(**CREATE_PLAN_SAVE)

        # Execute sub-chain
        create_plan_sequence_node = root.add_node(**EXECUTE_PLAN_SEQUENCE)
        create_plan_sequence_node.add_child(**EXECUTE_RUN)

        Agent.objects.get_or_create(
            id=PLANNER_AGENT_V3,
            defaults=dict(
                name="Planner v3",
                alias="plan",
                purpose="To generate plans for user requests.",
                chain=chain,
                config={},
            ),
        )
