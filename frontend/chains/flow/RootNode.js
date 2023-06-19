import React from "react";
import { Box, Heading } from "@chakra-ui/react";
import { Handle } from "reactflow";
import { faKeyboard } from "@fortawesome/free-solid-svg-icons";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const RootNode = () => {
  const { node, bg } = useEditorColorMode();

  return (
    <Box
      borderWidth="0px"
      borderRadius={8}
      padding="0"
      border="1px solid"
      borderColor="blue.800"
      backgroundColor={bg}
      minWidth={150}
    >
      <Handle
        id="out"
        type="source"
        position="right"
        style={{ top: "15px", transform: "translateX(-2px)" }}
      />
      <Heading
        as="h4"
        size="xs"
        color={node.root.color}
        borderRadius={7}
        bg={node.root.bg}
        px={1}
        py={2}
        className="drag-handle"
      >
        <FontAwesomeIcon icon={faKeyboard} /> Chat Input
      </Heading>
    </Box>
  );
};
