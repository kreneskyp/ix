import React from "react";
import { Box, HStack, Text, Tooltip } from "@chakra-ui/react";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const MenuItem = ({ children, wtf, title, ...props }) => {
  const { menu_icon } = useEditorColorMode();
  return (
    <Tooltip label={title} aria-label={title}>
      <HStack
        {...menu_icon}
        overflow="hidden"
        w={"100%"}
        align="center"
        {...props}
        cursor={"pointer"}
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
