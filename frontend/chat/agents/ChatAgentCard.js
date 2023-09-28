import React from "react";

import { AgentCard } from "chat/agents/AgentCard";
import { AgentToggleButton } from "chat/agents/AgentToggleButton";

export const ChatAgentCard = ({ agent, ...props }) => {
  return (
    <AgentCard agent={agent} {...props}>
      <AgentToggleButton agent={agent} />
    </AgentCard>
  );
};
