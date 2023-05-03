import React from "react";
import { Handle } from "reactflow";
import { Box, VStack, Heading, Text, Divider, HStack } from "@chakra-ui/react";
import { llm_name } from "chains/utils";

export const ChainNode = ({ data }) => {
  const node = data.node;
  const inputs = null;
  const outputs = null;
  return (
    <Box
      borderWidth="0px"
      borderRadius="lg"
      borderColor="rgba(100, 100, 150, 0.9)"
      padding="0"
      backgroundColor="rgba(80, 80, 150, 0.4)"
      width={250}
      color="rgba(255, 255, 255, 0.6)"
    >
      <Heading
        as="h4"
        size="xs"
        borderTopLeftRadius="lg"
        borderTopRightRadius="lg"
        bg="rgba(100, 100, 250, 0.6)"
        px={1}
        py={2}
      >
        {node.name || node.classPath.split(".").pop()}
      </Heading>
      <VStack spacing={0} alignItems="stretch">
        <Box>
          <strong>LLM: </strong>
          {llm_name(node.config?.llm?.class_path)}
        </Box>
        <Text pb={2}></Text>
        <Box position="relative">
          <Handle
            id="in"
            type="target"
            position="left"
            style={{ top: "50%", transform: "translateY(-50%)" }}
          />
          <Heading size="sm" px={2} bg="rgba(80, 80, 150, 0.2)">
            Inputs
          </Heading>
        </Box>
        <VStack alignItems="stretch">
          {inputs?.map((input, index) => (
            <HStack key={index} spacing="2">
              <Text>{input}</Text>
            </HStack>
          ))}
        </VStack>
        <Box position="relative">
          <Handle
            id="out"
            type="source"
            position="right"
            style={{ top: "50%", transform: "translateY(-50%)" }}
          />
          <Heading size="sm" px={2} bg="rgba(80, 80, 150, 0.2)">
            Output
          </Heading>
        </Box>
        <VStack alignItems="stretch" pb={2}>
          {outputs?.map((output, index) => (
            <HStack key={index} spacing="2">
              <Text>{output}</Text>
              <Handle type="source" position="bottom" id={`output-${index}`} />
            </HStack>
          ))}
        </VStack>
      </VStack>
    </Box>
  );
};

export default ChainNode;
