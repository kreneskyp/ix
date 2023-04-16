import React, { useState } from "react";
import {
  Button,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  useToast,
} from "@chakra-ui/react";
import { AgentEditor } from "agents/AgentEditor";
import { useMutation } from "react-relay/hooks";
import { UpdateAgentMutation } from "agents/graphql/AgentMutations";

export const AgentDetailModal = ({ agent, isOpen, onClose }) => {
  const [commit] = useMutation(UpdateAgentMutation);
  const [agentData, setAgentData] = useState(agent);
  const toast = useToast();

  const updateAgent = () => {
    const input = {
      ...agentData,
      config: agentData.config,
    };
    commit({
      variables: { input },
      onCompleted: () => {
        toast({
          title: "Saved",
          description: "Saved agent.",
          status: "success",
          duration: 3000,
          isClosable: true,
        });
      },
      onError: () => {
        toast({
          title: "Error",
          description: "Failed to save the agent.",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      },
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size={"3xl"}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Agent: {agent.name}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <AgentEditor
            agent={agent}
            agentData={agentData}
            setAgentData={setAgentData}
          />
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="blue" mr={3} onClick={onClose}>
            Close
          </Button>
          <Button colorScheme="green" onClick={updateAgent}>
            Save
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
