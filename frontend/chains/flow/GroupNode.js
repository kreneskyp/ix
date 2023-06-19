import React from "react";
import { Handle } from "reactflow";
import { Box, Heading } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { faChain } from "@fortawesome/free-solid-svg-icons";

// Dimensions of ChainNodes and layout
const CHAIN_NODE_WIDTH = 250;
const NODE_SPACER = 50;
const CONTAINER_MARGIN = 10;

export const GroupNode = ({ data }) => {
  const { type, node, children } = data;
  const { highlight, highlightColor } = useEditorColorMode();

  // calculate width to fit children.
  // if no children default to the size of one child.
  const width =
    (children.length - 1) * (CHAIN_NODE_WIDTH + NODE_SPACER) +
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
      <Heading
        as="h4"
        size="xs"
        color={highlightColor}
        borderTopLeftRadius={7}
        borderTopRightRadius={7}
        bg={highlight[type.type]}
        px={1}
        py={2}
        className="drag-handle"
      >
        <FontAwesomeIcon icon={faChain} /> {node.name}
      </Heading>
      <Handle id="in" type="target" position="left" />
      <Handle id="out" type="source" position="right" />
    </Box>
  );
};

export default GroupNode;
