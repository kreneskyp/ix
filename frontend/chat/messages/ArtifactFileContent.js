import React from "react";
import { Box, Text } from "@chakra-ui/react";
import SyntaxHighlighter from "react-syntax-highlighter";
import {
  stackoverflowDark,
  stackoverflowLight,
} from "react-syntax-highlighter/dist/cjs/styles/hljs";
import { useColorMode } from "@chakra-ui/color-mode";

export const ArtifactFileContent = ({ message }) => {
  const { colorMode } = useColorMode();
  const syntaxTheme =
    colorMode === "light" ? stackoverflowLight : stackoverflowDark;

  return (
    <Box my={4}>
      <Text color="blue.300">{message.content.storage.id}</Text>
      <SyntaxHighlighter style={syntaxTheme} wrapLines={true}>
        {message.content.data}
      </SyntaxHighlighter>
    </Box>
  );
};
