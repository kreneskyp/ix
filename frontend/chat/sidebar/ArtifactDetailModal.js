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
  Text,
  Tooltip,
} from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faDownload } from '@fortawesome/free-solid-svg-icons';
import ArtifactDetail from "chat/sidebar/ArtifactDetail";

export const ArtifactDetailModal = ({ artifact, isOpen, onClose }) => {
  const [hasOpened, setHasOpened] = useState(false);
  const { colorMode } = useColorMode;
  const color = colorMode === "light" ? "gray.800" : "gray.400";

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
          <Tooltip label="Download file">
            <Text as="span" color={color}>
              <FontAwesomeIcon
                icon={faDownload}
                style={{ marginLeft: '10px', cursor: "pointer" }}
                onClick={() => {
                  const url = `/api/artifacts/${artifact.id}/download`;
                  const link = document.createElement('a');
                  link.href = url;
                  link.setAttribute('download', 'file');
                  document.body.appendChild(link);
                  link.click();
                }}
            />
            </Text>
            </Tooltip>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <ArtifactDetail artifact={artifact} />
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};
