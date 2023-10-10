import React, { useCallback, useEffect, useState } from "react";
import { HStack, VStack, Box, Text, FormLabel } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faDiamond,
  faFile,
  faListCheck,
} from "@fortawesome/free-solid-svg-icons";
import ArtifactModalButton from "chat/sidebar/ArtifactModalButton";
import { useChatArtifactSubscription } from "chat/hooks/useChatArtifactSubscription";
import { SCROLLBAR_CSS } from "site/css";
import { FileDropZone } from "components/FileDropZone";

const ARTIFACT_TYPE_ICONS = {
  file: faFile,
  PLAN: faListCheck,
};

const TypeIcon = ({ artifact }) => {
  const icon = ARTIFACT_TYPE_ICONS[artifact.artifactType] || faDiamond;
  return <FontAwesomeIcon icon={icon} />;
};

const SideBarSubtext = ({ children, ...props }) => {
  const { colorMode } = useColorMode();
  const style = {
    fontSize: "xs",
    color: colorMode === "light" ? "gray.800" : "gray.500",
    borderRadius: "5px",
    p: 2,
    border: "1px solid",
    borderColor: colorMode === "light" ? "gray.300" : "gray.600",
    bg: colorMode === "light" ? "gray.100" : "gray.800",
    width: "100%",
  };
  return (
    <Text {...style} {...props}>
      {children}
    </Text>
  );
};

const SideBarArtifactList = ({ chat, artifacts: initialArtifacts }) => {
  const [artifacts, setArtifacts] = useState(initialArtifacts);

  // Reset artifacts when chat.id changes
  useEffect(() => {
    setArtifacts(initialArtifacts);
  }, [chat.id]);

  const { colorMode } = useColorMode();

  // Handle incoming new messages and update message groups
  const handleNewArtifact = useCallback((artifact) => {
    setArtifacts((prevArtifacts) => {
      return [...(prevArtifacts || []), artifact];
    });
  }, []);

  // subscribe to messages
  const subscriptionActive = useChatArtifactSubscription(
    chat.id,
    handleNewArtifact
  );

  return (
    <Box width="100%" minWidth={170} overflowY={"hidden"} height={"100vh"}>
      <FormLabel as="h3" size="md" align="left">
        Artifacts
      </FormLabel>
      <FileDropZone task_id={chat.task_id}>
        <VStack
          overflowY="scroll"
          css={SCROLLBAR_CSS}
          spacing={2}
          width="100%"
          height={"calc(100vh - 150px)"}
        >
          {!artifacts || artifacts?.length === 0 ? (
            <SideBarSubtext>
              Artifacts will appear here as they are created by agents.
            </SideBarSubtext>
          ) : null}
          {artifacts?.map((artifact, i) => (
            <Box
              key={i}
              bg="transparent"
              color={colorMode === "light" ? "gray.700" : "gray.400"}
              _hover={{
                bg: colorMode === "light" ? "gray.300" : "gray.700",
                cursor: "pointer",
              }}
              width="100%"
            >
              <ArtifactModalButton artifact={artifact}>
                <HStack justify="left" py={1} pl={2} width="100%">
                  <TypeIcon artifact={artifact} />
                  <span style={{ marginLeft: 10 }}>{artifact.name}</span>
                </HStack>
              </ArtifactModalButton>
            </Box>
          ))}
          <SideBarSubtext mt={2} border={"1px dashed"} bg="transparent">
            Drop files here to upload
          </SideBarSubtext>
        </VStack>
      </FileDropZone>
    </Box>
  );
};

export default SideBarArtifactList;
