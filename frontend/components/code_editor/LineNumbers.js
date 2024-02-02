import React from "react";
import { useSlate } from "slate-react";
import { Box } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/react";

export const LineNumbers = () => {
  const editor = useSlate();
  const element = editor.children[0];
  const lines = element.children || [];
  const { colorMode } = useColorMode();
  const bg = colorMode === "light" ? "blackAlpha.100" : "blackAlpha.300";

  return (
    <Box
      display="flex"
      flexDirection="column"
      borderTopLeftRadius={5}
      borderBottomLeftRadius={5}
      bg={bg}
      px={1}
      py={2}
      fontSize="xs"
      fontFamily="monospace"
    >
      {lines.map((_, index) => (
        <Box
          key={index}
          w="full"
          h="21px"
          m={0}
          display="flex"
          alignItems="end"
          justifyContent="flex-end"
        >
          {index + 1}
        </Box>
      ))}
    </Box>
  );
};
