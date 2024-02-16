import React from "react";
import { Box } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChain } from "@fortawesome/free-solid-svg-icons";
import { DraggableNode } from "chains/editor/DraggableNode";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const DraggableButton = ({
  name,
  description,
  config,
  class_path,
  highlight = "blue.300",
  label = "Reference",
}) => {
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
      name={name}
      description={description}
      config={config}
      class_path={class_path}
    >
      <Box
        p={2}
        h={8}
        borderRadius={5}
        borderLeft={"6px solid"}
        borderColor={highlight}
        fontSize={"sm"}
        display={"flex"}
        alignItems={"center"}
        {...style}
      >
        <FontAwesomeIcon icon={faChain} style={{ marginRight: "5px" }} />{" "}
        {label}
      </Box>
    </DraggableNode>
  );
};
