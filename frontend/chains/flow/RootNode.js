import React from "react";
import { VStack } from "@chakra-ui/react";
import { OutputsConnectors } from "chains/flow/FlowNode";

export const RootNode = ({ node }) => {
  return (
    <VStack spacing={0} alignItems="stretch" fontSize="xs">
      <OutputsConnectors node={node} />
    </VStack>
  );
};
