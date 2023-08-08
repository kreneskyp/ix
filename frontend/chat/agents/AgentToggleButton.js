import React, { useCallback, useState } from "react";
import axios from "axios";

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

export const AgentToggleButton = ({
  children,
  chat,
  chatAgents,
  agent,
  onSuccess,
}) => {
  const isAgentInChat = chatAgents.some((a) => a.id === agent.id);
  const { addAgent, removeAgent } = useAddRemoveAgent(chat, agent);

  const handleClick = () => {
    if (chat.lead_id === agent.id) {
      // If the agent is the lead, do nothing
      return;
    }

    let result;
    if (isAgentInChat) {
      result = removeAgent();
    } else {
      result = addAgent();
    }
    if (onSuccess) {
      onSuccess(result);
    }
  };

  return (
    <div onClick={handleClick} style={{ cursor: "pointer" }}>
      {children}
    </div>
  );
};
