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
  Box,
} from "@chakra-ui/react";
import { useDeleteAPI } from "utils/hooks/useDeleteAPI";

export const RemoveAgentModalTrigger = ({
  chat,
  agent,
  children,
  onSuccess,
  ...props
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const { call: callDelete, isLoading } = useDeleteAPI(
    `/api/chats/${chat.id}/agents/${agent.id}`
  );

  const handleClick = () => setIsOpen(true);
  const handleClose = () => setIsOpen(false);
  const handleConfirm = async () => {
    try {
      await callDelete();
      setIsOpen(false);
      onSuccess();
    } catch (err) {
      console.error(err);
    }
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
              isLoading={isLoading}
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
