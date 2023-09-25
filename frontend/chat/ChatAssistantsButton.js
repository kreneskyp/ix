import { IconButton } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAddressBook } from "@fortawesome/free-solid-svg-icons";
import React from "react";
import { useSideBarColorMode } from "chains/editor/useColorMode";
import AddAgentModalTrigger from "chat/agents/AddAgentModalTrigger";

export const ChatAssistantsButton = ({ graph, onUpdateAgents, agentPage }) => {
  const style = useSideBarColorMode();
  const agents = agentPage?.objects;

  return (
    <AddAgentModalTrigger
      graph={graph}
      chatAgents={agents}
      onSuccess={onUpdateAgents}
    >
      <IconButton
        icon={<FontAwesomeIcon icon={faAddressBook} />}
        title={"add/remove assistants"}
        {...style.button}
      />
    </AddAgentModalTrigger>
  );
};
