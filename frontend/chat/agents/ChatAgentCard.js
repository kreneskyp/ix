import React from "react";

import { AgentCard } from "agents/AgentCard";
import { AgentToggleButton } from "chat/agents/AgentToggleButton";
import { AgentEditButton } from "agents/AgentEditButton";

export const ChatAgentCard = ({ agent, ...props }) => {
  return (
    <AgentCard agent={agent} {...props}>
      <AgentEditButton agent={agent} />
      <AgentToggleButton agent={agent} />
    </AgentCard>
  );
};
