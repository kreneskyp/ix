import React, { useState } from "react";
import { useQueryLoader, usePreloadedQuery, graphql } from "react-relay/hooks";
import {
  Button,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Input,
  InputGroup,
  InputLeftElement,
  VStack,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSearch } from "@fortawesome/free-solid-svg-icons";
import { AddAgentCard } from "chat/agents/AddAgentCard";
import { AgentToggleButton } from "chat/agents/AgentToggleButton";

const AGENTS_QUERY = graphql`
  query AddAgentModalTriggerQuery($search: String) {
    searchAgents(search: $search) {
      id
      name
      alias
      purpose
      chain {
        id
        name
        description
      }
    }
  }
`;

const AddAgentModal = ({
  chat,
  isOpen,
  onClose,
  loadQuery,
  queryReference,
}) => {
  const data = usePreloadedQuery(AGENTS_QUERY, queryReference);
  const [search, setSearch] = useState("");

  const handleSearch = (event) => {
    setSearch(event.target.value);
    loadQuery({ search: event.target.value }); // Load agents that match the search
  };

  const agents = data?.searchAgents;
  const agentSet = new Set(chat?.agents?.map((agent) => agent.id));

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="2xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Manage Agents</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack maxH="md" overflowY="auto" spacing={5}>
            {agents?.map((agent) => (
              <AgentToggleButton chat={chat} agent={agent} key={agent.id}>
                <AddAgentCard
                  agent={agent}
                  inChat={agentSet.has(agent.id)}
                  isLead={agent.id === chat.lead.id}
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

export const AddAgentModalTrigger = ({ chat, children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [queryReference, loadQuery, disposeQuery] =
    useQueryLoader(AGENTS_QUERY);

  const handleClick = () => {
    loadQuery({ search: "" }); // Load initial agents
    setIsOpen(true);
  };

  const handleClose = () => {
    disposeQuery(); // Dispose of the query data when closing the modal
    setIsOpen(false);
  };

  return (
    <div onClick={handleClick} style={{ cursor: "pointer" }}>
      {children}
      {isOpen && (
        <AddAgentModal
          chat={chat}
          isOpen={isOpen}
          onClose={handleClose}
          queryReference={queryReference}
          loadQuery={loadQuery}
        />
      )}
    </div>
  );
};

export default AddAgentModalTrigger;
