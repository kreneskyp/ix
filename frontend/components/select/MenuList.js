import React from "react";
import { Box } from "@chakra-ui/react";
import { components } from "react-select";

import { useEditorColorMode } from "chains/editor/useColorMode";

export const MenuList = ({ children, ...props }) => {
  const { isLight } = useEditorColorMode();
  const style = isLight
    ? {
        bg: "white",
        border: "0px solid",
        borderColor: "gray.200",
        boxShadow: "0 0 10px rgba(0,0,0,0.5)",
      }
    : {
        bg: "gray.800",
        border: "0px solid",
        borderColor: "gray.600",
        boxShadow: "0 0 10px rgba(0,0,0,0.5)",
      };

  return (
    <components.MenuList {...props}>
      <Box {...style} mx={1}>
        {children}
      </Box>
    </components.MenuList>
  );
};
