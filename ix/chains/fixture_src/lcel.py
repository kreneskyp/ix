from ix.api.components.types import NodeTypeField
from ix.chains.fixture_src.targets import WORKFLOW_SOURCE, RUNNABLE_TYPES

RUNNABLE_PASS_THROUGH_CLASS_PATH = "ix.chains.components.lcel.init_pass_through"
RUNNABLE_PASS_THROUGH = {
    "class_path": RUNNABLE_PASS_THROUGH_CLASS_PATH,
    "name": "Pass Through",
    "description": "Passes inputs through to outputs",
    "type": "chain",
}


RUNNABLE_SEQUENCE_CLASS_PATH = "ix.chains.components.lcel.init_sequence"
RUNNABLE_SEQUENCE = {
    "class_path": RUNNABLE_SEQUENCE_CLASS_PATH,
    "name": "Runnable Sequence",
    "description": "Executes a sequence of runnables (chains, agents, prompts, tools, etc.)",
    "type": "sequence",
    "child_field": "steps",
    "connectors": [
        {
            "key": "steps",
            "type": "target",
            "source_type": RUNNABLE_TYPES,
            "required": False,
            "collection": "flow",
        },
    ],
}


RUNNABLE_MAP_CLASS_PATH = "ix.chains.components.lcel.init_parallel"
RUNNABLE_MAP = {
    "class_path": RUNNABLE_MAP_CLASS_PATH,
    "name": "Map Input",
    "description": "Map inputs to the output of flow branches (chains, agents, prompts, tools, etc.)",
    "type": "map",
    "fields": [
        NodeTypeField(
            name="steps",
            label="Input Branches",
            type="list",
            input_type="node_map_list",
            description="Input variables mapped from the output of the branch connected to it.",
            required=True,
        ).model_dump(),
        NodeTypeField(
            name="steps_hash",
            type="list",
            input_type="hidden",
            description="Input variables hashes in order they should be displayed. These hashes are "
            "used for connector identifiers. The step names may change without requiring"
            " edges to update unless the step is removed. Must be same length as steps. ",
            required=True,
        ).model_dump(),
    ],
}


RUNNABLE_BRANCH_CLASS_PATH = "ix.chains.components.lcel.init_branch"
RUNNABLE_BRANCH = {
    "class_path": RUNNABLE_BRANCH_CLASS_PATH,
    "name": "Choose Path",
    "description": "Executes the first branch whose input key is True, or default if none are True.",
    "type": "branch",
    "fields": [
        NodeTypeField(
            name="branches",
            label="Branch Variables",
            type="list",
            input_type="node_branch_list",
            description="input variables corresponding to branches in the order they will be "
            "considered. The first branch whose input variable is True will be "
            "executed. If none are True, the default branch will be executed.",
            required=True,
        ).model_dump(),
        NodeTypeField(
            name="branches_hash",
            type="list",
            input_type="hidden",
            description="Hashes for branches in order they should be displayed. These hashes "
            "are used for connector identifiers. The step names may change without "
            "requiring edges to update unless the step is removed. Must be same "
            "length as branches.",
            required=True,
        ).model_dump(),
    ],
}


RUNNABLE_EACH_CLASS_PATH = "ix.chains.components.lcel.init_each"
RUNNABLE_EACH = {
    "class_path": RUNNABLE_EACH_CLASS_PATH,
    "name": "Each",
    "description": "Executes a sub-workflow for each input in a list of inputs",
    "type": "flow",
    "connectors": [WORKFLOW_SOURCE],
}


RUNNABLE_PROXY_CLASS_PATH = "ix.chains.components.lcel.init_proxy"
RUNNABLE_PROXY = {
    "class_path": RUNNABLE_PROXY_CLASS_PATH,
    "name": "Proxy",
    "description": "Proxy to another runnable",
    "type": "proxy",
}


LANGCHAIN_RUNNABLES = [
    RUNNABLE_PASS_THROUGH,
    RUNNABLE_SEQUENCE,
    RUNNABLE_MAP,
    RUNNABLE_BRANCH,
    RUNNABLE_EACH,
    LANGGRAPH_STATE_MACHINE,
    # TODO:
    # LANGGRAPH_END,
]
