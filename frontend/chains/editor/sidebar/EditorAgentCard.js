import React from "react";
import { HStack } from "@chakra-ui/react";
import { AgentCard } from "agents/AgentCard";
import { ModalClose } from "components/Modal";
import { AgentEditButton } from "agents/AgentEditButton";
import { DraggableButton } from "chains/DraggableButton";

export const EditorAgentCard = ({ agent, ...props }) => {
  const close = React.useContext(ModalClose);

  return (
    <AgentCard agent={agent} {...props}>
      <HStack spacing={2} pt={4} display="flex" justifyContent="flex-end">
        <DraggableButton
          name={agent.name}
          description={agent.description}
          config={{ chain_id: agent.chain_id }}
          class_path="ix.runnable.flow.load_agent_id"
          label="Reference"
          highlight={"green.400"}
        />
        <AgentEditButton agent={agent} onClick={close} />
      </HStack>
    </AgentCard>
  );
};
