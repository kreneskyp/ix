import React from "react";
import ReactDOM from "react-dom";
import { Box } from "@chakra-ui/react";

/**
 * Basic overlay that renders a box. Renders in portal to break out of other layers.
 */
export const Overlay = ({ isOpen, onClose, ...props }) => {
  const handleClick = (event) => {
    event.stopPropagation();
    onClose();
  };

  return isOpen
    ? ReactDOM.createPortal(
        <Box
          position="fixed"
          top="0"
          right="0"
          bottom="0"
          left="0"
          zIndex="1"
          onClick={handleClick}
          {...props}
        />,
        document.getElementById("overlay")
      )
    : null;
};
