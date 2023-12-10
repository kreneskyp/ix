import React from "react";
import { Box } from "@chakra-ui/react";

export const StackableIcon = ({ children, ...props }) => {
  return (
    <Box
      w={"18px"}
      px={2}
      h={"30px"}
      position="relative"
      fontSize={"18px"}
      {...props}
    >
      <Box
        position="absolute"
        top="50%"
        left="50%"
        transform="translate(-50%, -50%)"
      >
        {children}
      </Box>
    </Box>
  );
};
