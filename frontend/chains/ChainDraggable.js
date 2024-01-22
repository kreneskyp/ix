import React from "react";
import { Box } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChain } from "@fortawesome/free-solid-svg-icons";
import { DraggableNode } from "chains/editor/DraggableNode";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const ChainDraggable = ({ chain }) => {
  const { isLight } = useEditorColorMode();
  const style = isLight
    ? {
        bg: "gray.100",
        _hover: { bg: "gray.300" },
      }
    : {
        bg: "whiteAlpha.200",
        _hover: { bg: "whiteAlpha.300" },
      };

  return (
    <DraggableNode
      name={chain.name}
      description={chain.description}
      config={{ chain_id: chain.id }}
      class_path="ix.runnable.flow.load_chain_id"
    >
      <Box
        p={2}
        h={8}
        borderRadius={5}
        borderLeft={"6px solid"}
        borderColor={"blue.300"}
        fontSize={"sm"}
        display={"flex"}
        alignItems={"center"}
        {...style}
      >
        <FontAwesomeIcon icon={faChain} style={{ marginRight: "5px" }} />{" "}
        Reference
      </Box>
    </DraggableNode>
  );
};
