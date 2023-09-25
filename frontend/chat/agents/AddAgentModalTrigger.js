import React, { useState } from "react";
import {
  Button,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  SimpleGrid,
  Box,
} from "@chakra-ui/react";
import { AddAgentCard } from "chat/agents/AddAgentCard";
import { AgentToggleButton } from "chat/agents/AgentToggleButton";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";
import { useEditorColorMode } from "chains/editor/useColorMode";

const AddAgentModal = ({
  graph,
  chatAgents,
  agents,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [search, setSearch] = useState("");
  const { chat } = graph;
  const { scrollbar } = useEditorColorMode();

  const handleSearch = (event) => {
    setSearch(event.target.value);
    loadQuery({ search: event.target.value }); // Load agents that match the search
  };

  const agentSet = new Set(chatAgents?.map((agent) => agent.id));

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="6xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Manage Agents</ModalHeader>
        <ModalCloseButton />
        <ModalBody p={0}>
          <Box
            maxH="calc(100vh - 250px)"
            overflowY="auto"
            spacing={5}
            css={scrollbar}
            px={3}
          >
            <SimpleGrid
              columns={[1, 2, 3]} // Responsive column setup
              spacing="20px"
              minChildWidth="360px" // Minimum width for each grid item
            >
              {agents?.map((agent) => (
                <AgentToggleButton
                  chat={chat}
                  chatAgents={chatAgents}
                  agent={agent}
                  key={agent.id}
                  onSuccess={onSuccess}
                >
                  <AddAgentCard
                    agent={agent}
                    inChat={agentSet.has(agent.id)}
                    isLead={agent.id === chat.lead_id}
                  />
                </AgentToggleButton>
              ))}
            </SimpleGrid>
          </Box>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" onClick={onClose}>
            Close
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export const AddAgentModalTrigger = ({
  graph,
  chatAgents,
  onSuccess,
  children,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const { page, load } = usePaginatedAPI("/api/agents/", {
    limit: 1000,
    load: false,
  });

  const handleClick = () => {
    load(); // Load initial agents
    setIsOpen(true);
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  return (
    <div onClick={handleClick} style={{ cursor: "pointer" }}>
      {children}
      {isOpen && (
        <AddAgentModal
          graph={graph}
          chatAgents={chatAgents}
          agents={page?.objects}
          isOpen={isOpen}
          onClose={handleClose}
          onSuccess={onSuccess}
        />
      )}
    </div>
  );
};

export default AddAgentModalTrigger;
