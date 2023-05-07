import React from "react";
import { HStack, VStack, Heading, Box } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faDiamond,
  faFile,
  faListCheck,
} from "@fortawesome/free-solid-svg-icons";
import { usePreloadedQuery } from "react-relay/hooks";
import { ChatByIdQuery } from "chat/graphql/ChatByIdQuery";
import ArtifactModalButton from "chat/sidebar/ArtifactModalButton";

const ARTIFACT_TYPE_ICONS = {
  file: faFile,
  PLAN: faListCheck,
};

const TypeIcon = ({ artifact }) => {
  const icon = ARTIFACT_TYPE_ICONS[artifact.artifactType] || faDiamond;
  return <FontAwesomeIcon icon={icon} />;
};

const SideBarArtifactList = ({ queryRef }) => {
  const { chat } = usePreloadedQuery(ChatByIdQuery, queryRef);
  const artifacts = chat.task.artifacts;
  const { colorMode } = useColorMode();

  return (
    <VStack spacing={1}>
      <Heading as="h3" size="md" width="100%" align="left" mt={5}>
        Artifacts
      </Heading>
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
    </VStack>
  );
};

export default SideBarArtifactList;
