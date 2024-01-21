import React from "react";
import { Box } from "@chakra-ui/react";

/**
 * Generic wrapper component that make a react component drag-n-droppable into the graph.
 * can be configured with a class_path, name, description, and config for the node that
 * will be created.
 *
 * This is used to create draggable nodes in the sidebar for objects like schmeas, agents,
 * and chains. The dropped nodes may be initialized with a config that references the
 * object that was dragged in.
 */
export const DraggableNode = ({
  children,
  name,
  description,
  class_path,
  config,
  onDrag,
  ...props
}) => {
  const handleStart = (event) => {
    const payload = {
      name,
      description,
      class_path,
      config,
    };
    event.dataTransfer.setData(
      "application/reactflow",
      JSON.stringify(payload)
    );
    event.dataTransfer.effectAllowed = "move";

    if (onDrag) {
      onDrag(payload);
    }
  };

  return (
    <Box cursor={"grab"} draggable onDragStart={handleStart} {...props}>
      {children}
    </Box>
  );
};
