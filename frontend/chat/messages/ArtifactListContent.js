import React from "react";
import {
  Box,
  Text,
  UnorderedList,
  ListItem,
  HStack,
  Heading,
} from "@chakra-ui/react";

export const ArtifactListContent = ({ message }) => {
  return (
    <Box>
      <Heading size="dm">Generating code:</Heading>
      <UnorderedList justify="start" mx={5}>
        {message.content.data.map((artifact, index) => (
          <ListItem key={index} align="top">
            <HStack align="top">
              <Text color="blue.300">{artifact.filename}</Text>
              <Text color="gray.100">- {artifact.description}</Text>
            </HStack>
          </ListItem>
        ))}
      </UnorderedList>
    </Box>
  );
};
