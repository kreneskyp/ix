import React, { useState } from "react";
import { useMutation } from "react-relay";
import {
  Button,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Box,
} from "@chakra-ui/react";
import RemoveAgentMutation from "chat/graphql/RemoveAgentMutation";

export const RemoveAgentModalTrigger = ({
  chat,
  agent,
  children,
  ...props
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [commitMutation, isInFlight] = useMutation(RemoveAgentMutation);

  const handleClick = () => setIsOpen(true);
  const handleClose = () => setIsOpen(false);

  const handleConfirm = () => {
    commitMutation({
      variables: { chatId: chat.id, agentId: agent.id },
      onCompleted: () => {
        setIsOpen(false);
      },
      onError: (err) => console.error(err),
    });
  };

  return (
    <Box {...props} onClick={handleClick} style={{ cursor: "pointer" }}>
      {children}
      <Modal isOpen={isOpen} onClose={handleClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Remove Agent</ModalHeader>
          <ModalCloseButton />
          <ModalBody>Are you sure you want to remove {agent.name}?</ModalBody>

          <ModalFooter>
            <Button
              colorScheme="blue"
              mr={3}
              onClick={handleConfirm}
              isLoading={isInFlight}
            >
              Yes
            </Button>
            <Button variant="ghost" onClick={handleClose}>
              No
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default RemoveAgentModalTrigger;
