import React, { useEffect, useState } from "react";
import {
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Tag,
  TagLabel,
} from "@chakra-ui/react";
import ArtifactDetail from "chat/sidebar/ArtifactDetail";

export const ArtifactDetailModal = ({ artifact, isOpen, onClose }) => {
  const [hasOpened, setHasOpened] = useState(false);

  useEffect(() => {
    if (!hasOpened) {
      setHasOpened(true);
    }
  }, [hasOpened]);

  return (
    <Modal isOpen={isOpen} onClose={onClose} size={"3xl"}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          {artifact.name}
          <Tag size="md" colorScheme="blue" ml={3} mt={1}>
            <TagLabel>{artifact.artifactType}</TagLabel>
          </Tag>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <ArtifactDetail artifact={artifact} />
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};
