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
import { MenuItem } from "site/MenuItem";

export const ModalClose = React.createContext(null);

export const GenericModal = ({
  title,
  isOpen,
  onClose,
  showClose,
  children,
  size,
}) => {
  const modalRef = React.useRef();

  const handleFocus = (event) => {
    if (modalRef.current && !modalRef.current.contains(event.target)) {
      onClose();
    }
  };

  React.useEffect(() => {
    if (isOpen) {
      document.addEventListener("focus", handleFocus, true);
    }
    return () => {
      document.removeEventListener("focus", handleFocus, true);
    };
  }, [isOpen, onClose]);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size={size}
      finalFocusRef={modalRef}
    >
      <ModalOverlay />
      <ModalContent ref={modalRef}>
        <ModalHeader>{title}</ModalHeader>
        <ModalCloseButton />
        <ModalBody p={0}>{children}</ModalBody>
        <ModalFooter>
          {showClose && (
            <Button variant="ghost" onClick={onClose}>
              Close
            </Button>
          )}
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

GenericModal.defaultProps = {
  showClose: true,
  size: "6xl",
};

export const ModalTriggerContent = ({ children }) => {
  return children;
};

export const ModalTriggerButton = ({ children }) => {
  return children;
};

export const ModalTrigger = ({
  onOpen,
  showClose,
  children,
  title,
  ...props
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const button = React.Children.toArray(children).find(
    (child) =>
      child.type === MenuItem ||
      child.type === ModalTriggerButton ||
      child.type === IconButton ||
      child.type === Button
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
    <ModalClose.Provider value={handleClose}>
      <div onClick={handleClick} style={{ cursor: "pointer" }}>
        {button}
      </div>
      {isOpen && (
        <GenericModal
          title={title}
          isOpen={isOpen}
          onClose={handleClose}
          showClose={showClose}
          {...props}
        >
          {content}
        </GenericModal>
      )}
    </ModalClose.Provider>
  );
};

ModalTrigger.Content = ModalTriggerContent;
ModalTrigger.Button = ModalTriggerButton;

ModalTrigger.defaultProps = {
  showClose: true,
};
