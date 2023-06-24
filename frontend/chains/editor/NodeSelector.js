import React from "react";
import { Box, Flex, Text } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBars } from "@fortawesome/free-solid-svg-icons";
import { useSideBarColorMode } from "chains/editor/useColorMode";

/**
 * Represents a node that can be dragged from the toolbar into the graph.
 * Expects a nodeSelectorConfig prop that contains the label of the node
 * and other configuration for creating the node in the graph.
 */
export const NodeSelector = ({ type }) => {
  const { isLight } = useSideBarColorMode();

  const handleStart = (event, data) => {
    event.dataTransfer.setData("application/reactflow", JSON.stringify(type));
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <Box
      p={1}
      m={2}
      minHeight={25}
      minWidth={150}
      width="95%"
      color={isLight ? "gray.800" : "gray.400"}
      bg={isLight ? "gray.100" : "gray.800"}
      border="1px solid"
      borderColor={isLight ? "gray.400" : "gray.700"}
      borderRadius={3}
      onDragStart={(event) => handleStart(event, "input")}
      cursor={"grab"}
      draggable
    >
      <Flex
        alignItems="center"
        justifyContent="space-between"
        width="100%"
        height="100%"
      >
        <Text fontSize="xs">{type.name}</Text>
        <FontAwesomeIcon size="xs" icon={faBars} />
      </Flex>
    </Box>
  );
};
