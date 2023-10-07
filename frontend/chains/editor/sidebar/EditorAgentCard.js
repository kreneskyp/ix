import React from "react";

import { AgentCard } from "agents/AgentCard";
import { ModalClose } from "components/Modal";
import { AgentEditButton } from "agents/AgentEditButton";

export const EditorAgentCard = ({ agent, ...props }) => {
  const close = React.useContext(ModalClose);

  return (
    <AgentCard agent={agent} {...props}>
      <AgentEditButton agent={agent} onClick={close} />
    </AgentCard>
  );
};
