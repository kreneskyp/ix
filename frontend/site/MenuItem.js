import React from "react";
import { Box, HStack, Text, Tooltip } from "@chakra-ui/react";

export const MenuItem = ({ children, wtf, title, ...props }) => {
  return (
    <Tooltip label={title} aria-label={title}>
      <HStack
        overflow="hidden"
        w={"100%"}
        align="center"
        {...props}
        cursor={"pointer"}
        _hover={{
          color: "gray.500",
        }}
      >
        <Box minW="25px" w={"25px"} pl={"2px"}>
          {children}
        </Box>
        <Text fontSize={"sm"} whiteSpace="nowrap">
          {title}
        </Text>
      </HStack>
    </Tooltip>
  );
};
