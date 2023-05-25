import React from "react";
import { Heading, Text, VStack } from "@chakra-ui/react";
import { useChatColorMode } from "chains/editor/useColorMode";

export const ArtifactSearchResults = ({ selected, results }) => {
  const artifacts = results;
  const { autoCompleteSelected } = useChatColorMode();

  return (
    <VStack align="left">
      <Heading as="h3" size="xs">
        Artifacts
      </Heading>
      {artifacts?.map((artifact, i) => {
        const bg = i === selected ? autoCompleteSelected : "transparent";
        return (
          <Text key={i} width="100%" bg={bg} p={2}>
            {artifact.key}
          </Text>
        );
      })}
    </VStack>
  );
};
