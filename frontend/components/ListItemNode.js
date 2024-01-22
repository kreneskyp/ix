import React from "react";
import { Box } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChain } from "@fortawesome/free-solid-svg-icons";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { getOptionStyle } from "chains/editor/NodeSelector";

/**
 * An expanding node for use in menu popover lists. When hovered, the node
 * expands to show the full label.
 *
 * This is normally combined with DraggableNode to create a node
 * that can be dragged into the graph.
 */
export const ListItemNode = ({ label, icon, expanded }) => {
  const { isLight, highlight } = useEditorColorMode();
  const style = getOptionStyle(isLight);

  return (
    <Box
      h={"100%"}
      w={10}
      bg={style.modal_hover}
      p={3}
      {...style.label}
      display={"flex"}
      alignItems={"center"}
      justifyContent={"center"}
      _hover={{
        borderLeft: "6px solid",
        borderLeftColor: highlight.chain,
        width: expanded,
        ".hover-text": { visibility: "visible", maxWidth: expanded - 10 },
      }}
      transition="background-color 0.2s ease-in, all 0.2s ease-in, width 0.2s ease-in"
      borderRadius={5}
      fontSize={"xs"}
      cursor={"grab"}
    >
      <FontAwesomeIcon icon={icon || faChain} />
      <Box
        as="span"
        className="hover-text"
        visibility="hidden"
        maxWidth="0"
        overflow="hidden"
        whiteSpace="nowrap"
        ml={2}
        transition="visibility 0.2s ease-in, max-width 0.2s ease-in"
      >
        {label}
      </Box>
    </Box>
  );
};

ListItemNode.defaultProps = {
  expanded: 130,
};
