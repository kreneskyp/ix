import React from "react";
import { Handle } from "reactflow";
import { Box, VStack, Heading, Text, Divider, HStack } from "@chakra-ui/react";

// Dimensions of ChainNodes and layout
const CHAIN_NODE_WIDTH = 250;
const NODE_SPACER = 50;
const CONTAINER_MARGIN = 10;

export const GroupNode = ({ data }) => {
  // calculate width to fit children.
  // if no children default to the size of one child.
  const width =
    (data.children.length - 1) * (CHAIN_NODE_WIDTH + NODE_SPACER) +
    CHAIN_NODE_WIDTH +
    CONTAINER_MARGIN * 2;

  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      borderColor="whiteAlpha.300"
      padding="0"
      backgroundColor="blackAlpha.500"
      height={165}
      width={width}
    >
      <Text pl={3}>{data.node.name}</Text>

      <Handle id="in" type="target" position="left" />
      <Handle id="out" type="source" position="right" />
    </Box>
  );
};

export default GroupNode;
