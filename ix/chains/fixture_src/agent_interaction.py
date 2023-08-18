from ix.api.chains.types import NodeTypeField
from ix.chains.agent_interaction import DelegateToAgentChain
from ix.chains.fixture_src.common import CHAIN_BASE_FIELDS
from ix.chains.fixture_src.targets import MEMORY_TARGET, PROMPT_TARGET


DELEGATE_TO_AGENT_CHAIN = {
    "class_path": "ix.chains.agent_interaction.DelegateToAgentChain",
    "name": "DelegateToAgent",
    "description": "Delegate a request to another agent. Does not wait for a response.",
    "type": "chain",
    "connectors": [MEMORY_TARGET, PROMPT_TARGET],
    "fields": CHAIN_BASE_FIELDS
    + NodeTypeField.get_fields_from_model(
        DelegateToAgentChain,
        include=[
            "output_key",
            "target_alias",
            "delegate_inputs",
        ],
    ),
}


AGENT_INTERACTION_CHAINS = [
    DELEGATE_TO_AGENT_CHAIN,
]


__all__ = [AGENT_INTERACTION_CHAINS, DELEGATE_TO_AGENT_CHAIN]
