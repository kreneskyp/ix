import { IconButton } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAddressBook } from "@fortawesome/free-solid-svg-icons";
import React, { useCallback, useEffect } from "react";
import { useSideBarColorMode } from "chains/editor/useColorMode";
import AddAgentModalTrigger from "chat/agents/AddAgentModalTrigger";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";

export const ChatAssistantsButton = ({ graph }) => {
  const style = useSideBarColorMode();

  const { load: loadAgents, page: agentPage } = usePaginatedAPI(
    `/api/agents/`,
    { limit: 10000, load: false }
  );
  const agents = agentPage?.objects;
  const queryArgs = { chat_id: graph.chat.id };
  const onUpdateAgents = useCallback(() => {
    loadAgents(queryArgs);
  }, [loadAgents]);

  useEffect(() => {
    loadAgents(queryArgs);
  }, [loadAgents, graph.chat.id]);

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
