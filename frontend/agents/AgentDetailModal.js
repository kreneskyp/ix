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
  return (
    <Modal isOpen={isOpen} onClose={onClose} size={"3xl"}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Agent: {agent.name}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <AgentEditor agent={agent} />
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};
