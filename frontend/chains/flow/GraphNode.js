import React from "react";
import { BranchConnectors, InputConnector } from "chains/flow/BranchNode";
import { VStack, Flex } from "@chakra-ui/react";
import { OutputConnector } from "chains/flow/ChainNode";

export const GraphNode = ({ type, node, config, onFieldChange }) => {
  return (
    <VStack spacing={0} alignItems="stretch" fontSize="xs">
      <Flex mt={1} mb={3} justify={"space-between"}>
        <InputConnector type={type} node={node} />
        <OutputConnector type={type} node={node} />
      </Flex>
      <Flex mt={1} mb={3} justify={"space-between"}>
        <InputConnector
          type={type}
          node={node}
          id={"loop"}
          label={"Loop"}
          required={false}
        />
        <BranchConnectors node={node} />
      </Flex>
    </VStack>
  );
};
