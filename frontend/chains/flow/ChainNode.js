import React from "react";
import { Handle } from "reactflow";
import { Box, VStack, Heading, Flex } from "@chakra-ui/react";
import { TypeAutoFields } from "chains/flow/TypeAutoFields";
import { CollapsibleSection } from "chains/flow/CollapsibleSection";
import { NodeProperties } from "chains/flow/ConfigNode";

export const ChainNode = ({ type, node, config, onFieldChange }) => {
  return (
    <VStack spacing={0} alignItems="stretch" fontSize="xs">
      <Flex mt={1} mb={3} justify={"space-between"}>
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
      </Flex>
      <NodeProperties type={type} />
      <CollapsibleSection title="Config">
        <TypeAutoFields type={type} config={config} onChange={onFieldChange} />
      </CollapsibleSection>
    </VStack>
  );
};
