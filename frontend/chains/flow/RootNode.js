import React from "react";
import { Box, Heading } from "@chakra-ui/react";
import { Handle } from "reactflow";
import { faKeyboard } from "@fortawesome/free-solid-svg-icons";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { ConnectorPopover } from "chains/editor/ConnectorPopover";

const ROOT_NODE = {
  id: "root",
};

const ROOT_CONNECTOR = {
  key: "out",
  type: "source",
  source_type: ["agent", "chain"],
  description: "Connect to an agent or chain input that starts the chain.",
};

const ROOT_TYPE = {
  id: "root",
  class_path: "root",
  fields: [],
  connectors: [ROOT_CONNECTOR],
};

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
      alignItems={"right"}
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
        <FontAwesomeIcon icon={faKeyboard} />{" "}
        <ConnectorPopover
          type={ROOT_TYPE}
          node={ROOT_NODE}
          connector={ROOT_CONNECTOR}
          label={"Chat Input"}
          placement={"right"}
        />
      </Heading>
    </Box>
  );
};
