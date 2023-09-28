import React, { useCallback, useState } from "react";
import axios from "axios";
import { Button, Switch } from "@chakra-ui/react";

import { ChatAgents, ChatGraph } from "chat/contexts";

export const useAddRemoveAgent = (chat, agent) => {
  const url = `/api/chats/${chat.id}/agents/${agent.id}`;
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const addAgent = useCallback(async () => {
    setIsLoading(true);
    try {
      await axios.put(url);
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, [url]);

  const removeAgent = useCallback(async () => {
    setIsLoading(true);
    try {
      await axios.delete(url);
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, [url]);

  return {
    addAgent,
    removeAgent,
    isLoading,
    error,
  };
};

export const AgentToggleButton = ({ agent }) => {
  const agentsAPI = React.useContext(ChatAgents);
  const { chat } = React.useContext(ChatGraph);
  const chatAgents = agentsAPI.page?.objects;
  const isAgentInChat = chatAgents.some((a) => a.id === agent.id);
  const { addAgent, removeAgent } = useAddRemoveAgent(chat, agent);
  const isLead = chat.lead_id === agent.id;

  const handleClick = () => {
    if (isLead) {
      // If the agent is the lead, do nothing
      return;
    }

    let request;
    if (isAgentInChat) {
      request = removeAgent();
    } else {
      request = addAgent();
    }
    request.then((result) => {
      agentsAPI.load({ chat_id: chat.id });
    });
  };

  const sx =
    isAgentInChat || isLead
      ? { borderColor: "blue.300" }
      : { borderColor: "transparent" };

  return (
    <Button
      size={"sm"}
      onClick={handleClick}
      disabled={isLead}
      border={"1px solid"}
      {...sx}
    >
      <Switch
        size={"sm"}
        colorScheme={"blue"}
        mr={2}
        isChecked={isAgentInChat || isLead}
        disabled={isLead}
      />
      Enable
    </Button>
  );
};
