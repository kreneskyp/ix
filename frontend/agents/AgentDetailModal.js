import React, { useEffect, useState } from "react";
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
import { useQueryLoader } from "react-relay";
import { ChainsQuery } from "chains/graphql/ChainsQuery";

export const AgentDetailModal = ({ agent, isOpen, onClose }) => {
  const [chainsRef, loadChains] = useQueryLoader(ChainsQuery);
  const [hasOpened, setHasOpened] = useState(false);

  useEffect(() => {
    if (!hasOpened) {
      loadChains();
      setHasOpened(true);
    }
  }, [hasOpened]);

  return (
    <Modal isOpen={isOpen} onClose={onClose} size={"3xl"}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Agent: {agent.name}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <AgentEditor agent={agent} chainsRef={chainsRef} />
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};
