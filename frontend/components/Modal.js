import React, { useState } from "react";
import {
  Button,
  IconButton,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
} from "@chakra-ui/react";

export const GenericModal = ({ title, isOpen, onClose, children }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="6xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>{title}</ModalHeader>
        <ModalCloseButton />
        <ModalBody p={0}>{children}</ModalBody>
        <ModalFooter>
          <Button variant="ghost" onClick={onClose}>
            Close
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export const ModalTriggerContent = ({ children }) => {
  return children;
};

export const ModalTrigger = ({ onOpen, children, title }) => {
  const [isOpen, setIsOpen] = useState(false);

  const button = React.Children.toArray(children).find(
    (child) => child.type === IconButton
  );
  const content = React.Children.toArray(children).find(
    (child) => child.type === ModalTriggerContent
  );

  const handleClick = () => {
    onOpen && onOpen();
    setIsOpen(true);
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  return (
    <div onClick={handleClick} style={{ cursor: "pointer" }}>
      {button}
      {isOpen && (
        <GenericModal title={title} isOpen={isOpen} onClose={handleClose}>
          {content}
        </GenericModal>
      )}
    </div>
  );
};

ModalTrigger.Content = ModalTriggerContent;
