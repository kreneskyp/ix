import React from "react";
import { Flex, Heading, Text, VStack } from "@chakra-ui/react";
import { useChatColorMode } from "chains/editor/useColorMode";

export const MentionSearchResults = ({ selected, results }) => {
  const agents = results;
  const { autoCompleteSelected, mention } = useChatColorMode();

  return (
    <VStack align="left">
      <Heading as="h3" size="xs">
        Agents
      </Heading>
      {agents?.map((agent, i) => {
        const bg = i === selected ? autoCompleteSelected : "transparent";
        return (
          <Flex
            key={i}
            bg={bg}
            width="100%"
            justifyContent="space-between"
            p={2}
          >
            <Text>{agent.name}</Text> <Text sx={mention}>@{agent.alias}</Text>
          </Flex>
        );
      })}
    </VStack>
  );
};
