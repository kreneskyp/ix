from ix.chains.fixture_src.targets import MEMORY_TARGET

SELECTION_CHAIN_TARGET = {
    "key": "selection_chain",
    "type": "target",
    "source_type": "chain",
}

CHAT_MODERATOR_TYPE = {
    "class_path": "ix.chains.moderator.ChatModerator",
    "name": "IX Chat Moderator",
    "description": "Chat moderator analyzes user input and delegates it to the appropriate agent.",
    "type": "chain",
    "display_type": "node",
    "connectors": [SELECTION_CHAIN_TARGET, MEMORY_TARGET],
}
