import React from "react";
import { Box, useDisclosure } from "@chakra-ui/react";
import { ArtifactDetailModal } from "chat/sidebar/ArtifactDetailModal";

export const ArtifactModalButton = ({ artifact, children }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  if (artifact == null) {
    return null;
  }

  return (
    <>
      <ArtifactDetailModal
        artifact={artifact}
        isOpen={isOpen}
        onClose={onClose}
      />
      <Box onClick={onOpen}>{children}</Box>
    </>
  );
};

export default ArtifactModalButton;
