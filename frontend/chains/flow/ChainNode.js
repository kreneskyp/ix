import React from "react";
import { Handle } from "reactflow";
import { Box, VStack, Heading, Text, HStack } from "@chakra-ui/react";
import { TypeAutoFields } from "chains/flow/TypeAutoFields";
import { CollapsibleSection } from "chains/flow/CollapsibleSection";
import { NodeProperties } from "chains/flow/ConfigNode";

export const ChainNode = ({ type, node, config, onFieldChange }) => {
  const inputs = null;
  const outputs = null;

  return (
    <VStack spacing={0} alignItems="stretch" fontSize="xs">
      <Box position="relative">
        <Handle
          id="in"
          type="target"
          position="left"
          style={{ top: "50%", transform: "translateY(-50%)" }}
        />
        <Heading fontSize="xs" px={2}>
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
        <Heading fontSize="xs" px={2}>
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
      <NodeProperties type={type} />
      <CollapsibleSection title="Config">
        <TypeAutoFields type={type} config={config} onChange={onFieldChange} />
      </CollapsibleSection>
    </VStack>
  );
};
