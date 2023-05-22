import React from "react";
import { Box, useDisclosure } from "@chakra-ui/react";
import { AgentDetailModal } from "agents/AgentDetailModal";

export const AgentDetailModalButton = ({ agent, children, ...props }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  return (
    <>
      <AgentDetailModal agent={agent} isOpen={isOpen} onClose={onClose} />
      <Box onClick={onOpen} {...props}>
        {children}
      </Box>
    </>
  );
};

export default AgentDetailModalButton;
