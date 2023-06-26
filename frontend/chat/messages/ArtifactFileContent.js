import React from "react";
import { Box, Text } from "@chakra-ui/react";
import SyntaxHighlighter from "react-syntax-highlighter";
import {
  stackoverflowDark,
  stackoverflowLight,
} from "react-syntax-highlighter/dist/cjs/styles/hljs";
import { useChatColorMode } from "chains/editor/useColorMode";

export const ArtifactFileContent = ({ message }) => {
  const { isLight, link } = useChatColorMode();
  const syntaxTheme = isLight ? stackoverflowLight : stackoverflowDark;

  return (
    <Box my={4}>
      <Text sx={link}>{message.content.storage.id}</Text>
      <SyntaxHighlighter style={syntaxTheme} wrapLines={true}>
        {message.content.data}
      </SyntaxHighlighter>
    </Box>
  );
};
