import React from "react";
import { Box, useDisclosure } from "@chakra-ui/react";
import { useAgent } from "agents/graphql/AgentProvider";
import { AgentDetailModal } from "agents/AgentDetailModal";
import AgentCard from "agents/AgentCard";

const AgentCardModalButton = () => {
  const { agent } = useAgent();
  const { isOpen, onOpen, onClose } = useDisclosure();

  if (agent == null) {
    return null;
  }

  return (
    <>
      <AgentDetailModal agent={agent} isOpen={isOpen} onClose={onClose} />
      <Box onClick={onOpen}>
        <AgentCard />
      </Box>
    </>
  );
};

export default AgentCardModalButton;
