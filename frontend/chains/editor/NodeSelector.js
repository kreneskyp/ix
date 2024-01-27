import React from "react";
import { Box, Text } from "@chakra-ui/react";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const getOptionStyle = (isLight) => {
  return isLight
    ? {
        default: {
          color: "gray.800",
          bg: "transparent",
        },
        disabled: {
          color: "gray.500",
          bg: "transparent",
        },
        hover: {
          bg: "blackAlpha.100",
          color: "gray.800",
        },
        label: {
          color: "gray.600",
          fontWeight: "bold",
          fontSize: "sm",
        },
        container: {
          color: "gray.700",
        },
        help: {
          color: "gray.500",
          fontSize: "xs",
        },
        icon: {
          color: "gray.600",
        },
        selected: {
          bg: "blackAlpha.100",
          color: "gray.800",
        },
      }
    : {
        default: {
          color: "white",
          bg: "transparent",
        },
        disabled: {
          bg: "transparent",
          color: "gray.500",
        },
        hover: {
          bg: "blackAlpha.300",
          color: "white",
        },
        label: {
          color: "gray.300",
          fontWeight: "bold",
          fontSize: "sm",
        },
        help: {
          color: "gray.500",
          fontSize: "xs",
        },
        icon: {
          color: "gray.300",
        },
        selected: {
          bg: "whiteAlpha.100",
          color: "gray.200",
        },
      };
};

/**
 * Represents a node that can be dragged from the toolbar into the graph.
 * Expects a nodeSelectorConfig prop that contains the label of the node
 * and other configuration for creating the node in the graph.
 */
export const NodeSelector = ({ type }) => {
  const { isLight, highlight } = useEditorColorMode();
  const style = getOptionStyle(isLight);

  const handleStart = (event, data) => {
    event.dataTransfer.setData(
      "application/reactflow",
      JSON.stringify({ type })
    );
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <Box
      p={1}
      m={2}
      mr={0}
      ml={0}
      pl={2}
      minHeight={25}
      width="100%"
      onDragStart={(event) => handleStart(event, "input")}
      cursor={"grab"}
      draggable
      borderLeft={"6px solid"}
      borderLeftColor={highlight[type.type]}
      borderRadius={5}
      _hover={style.hover}
    >
      <Box>
        <Text fontWeight="bold" fontSize={"sm"} {...style.label}>
          {type.name}
        </Text>
        <Text fontSize="xs" {...style.help}>
          {type.description}
        </Text>
      </Box>
    </Box>
  );
};
