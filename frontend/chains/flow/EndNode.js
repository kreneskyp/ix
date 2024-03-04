import React from "react";
import { VStack } from "@chakra-ui/react";
import { InputConnector } from "chains/flow/ChainNode";

const END_CONNECTOR = {
  key: "in",
  type: "target",
  source_type: ["agent", "chain"],
  description: "Connect to node that ends state machine.",
};

const END_TYPE = {
  id: "langgraph.graph.END",
  class_path: "graph_end",
  connectors: [END_CONNECTOR],
};

export const EndNode = ({ node }) => {
  return (
    <VStack spacing={0} alignItems="stretch" fontSize="xs">
      <InputConnector type={END_TYPE} node={node} />
    </VStack>
  );
};
