import React from "react";
import { useMutation } from "react-relay/hooks";
import { AddAgentMutation } from "chat/graphql/AddAgentMutation";
import RemoveAgentMutation from "chat/graphql/RemoveAgentMutation";

export const AgentToggleButton = ({ children, chat, agent }) => {
  const [commitAddMutation] = useMutation(AddAgentMutation);
  const [commitRemoveMutation] = useMutation(RemoveAgentMutation);

  const isAgentInChat = chat.agents.some((a) => a.id === agent.id);

  const handleClick = () => {
    if (chat.lead.id === agent.id) {
      // If the agent is the lead, do nothing
      return;
    }

    if (isAgentInChat) {
      commitRemoveMutation({
        variables: { chatId: chat.id, agentId: agent.id },
        onCompleted: () => console.log("Agent removed from chat"),
        onError: (err) => console.error(err),
      });
    } else {
      commitAddMutation({
        variables: { chatId: chat.id, agentId: agent.id },
        onCompleted: () => console.log("Agent added to chat"),
        onError: (err) => console.error(err),
      });
    }
  };

  return (
    <div onClick={handleClick} style={{ cursor: "pointer" }}>
      {children}
    </div>
  );
};
