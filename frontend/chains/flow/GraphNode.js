import React from "react";
import {
  BranchTarget,
  InputConnector,
  useFlowConnectors,
} from "chains/flow/BranchNode";
import { VStack, Flex } from "@chakra-ui/react";
import { OutputConnector } from "chains/flow/ChainNode";

export const GraphConnectors = ({ node }) => {
  const { branches } = useFlowConnectors(node);

  return (
    <Flex justify={"space-between"}>
      <VStack spacing={0} cursor="default"></VStack>
      <VStack>
        {branches?.map((connector, i) => (
          <BranchTarget key={connector.key} node={node} connector={connector} />
        ))}
      </VStack>
    </Flex>
  );
};

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
        <GraphConnectors node={node} />
      </Flex>
    </VStack>
  );
};
