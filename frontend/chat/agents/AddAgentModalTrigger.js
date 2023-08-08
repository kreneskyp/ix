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
  VStack,
} from "@chakra-ui/react";
import { AddAgentCard } from "chat/agents/AddAgentCard";
import { AgentToggleButton } from "chat/agents/AgentToggleButton";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";

const AddAgentModal = ({ graph, agents, isOpen, onClose, onSuccess }) => {
  const [search, setSearch] = useState("");
  const { chat } = graph;

  const handleSearch = (event) => {
    setSearch(event.target.value);
    loadQuery({ search: event.target.value }); // Load agents that match the search
  };

  const agentSet = new Set(graph?.agents?.map((agent) => agent.id));

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="2xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Manage Agents</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack maxH="md" overflowY="auto" spacing={5}>
            {agents?.map((agent) => (
              <AgentToggleButton
                chat={chat}
                chatAgents={graph.agents}
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
          </VStack>
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

export const AddAgentModalTrigger = ({ graph, onSuccess, children }) => {
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
