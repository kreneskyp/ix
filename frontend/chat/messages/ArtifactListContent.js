import React from "react";
import {
  Box,
  Text,
  UnorderedList,
  ListItem,
  HStack,
  Heading,
} from "@chakra-ui/react";
import { useChatColorMode } from "chains/editor/useColorMode";

export const ArtifactListContent = ({ message }) => {
  const { message: messageStyle, link } = useChatColorMode();
  return (
    <Box>
      <Heading size="dm">Generating code:</Heading>
      <UnorderedList justify="start" mx={5}>
        {message.content.data.map((artifact, index) => (
          <ListItem key={index} align="top">
            <HStack align="top">
              <Text sx={link}>{artifact.filename}</Text>
              <Text color={messageStyle.color}>- {artifact.description}</Text>
            </HStack>
          </ListItem>
        ))}
      </UnorderedList>
    </Box>
  );
};
