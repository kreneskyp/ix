import React, { useState, useEffect, useCallback } from "react";
import SyntaxHighlighter from "react-syntax-highlighter";
import {
  stackoverflowDark,
  stackoverflowLight,
} from "react-syntax-highlighter/dist/cjs/styles/hljs";
import { useColorMode, Box, Text } from "@chakra-ui/react";
import copy from "copy-to-clipboard";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faClipboard, faCheck } from "@fortawesome/free-solid-svg-icons";

export const HighlightedCode = ({ text }) => {
  const { colorMode } = useColorMode();
  const syntaxTheme =
    colorMode === "light" ? stackoverflowLight : stackoverflowDark;

  const style =
    colorMode === "light"
      ? { color: "gray.600", _hover: { color: "blue.400" } }
      : { color: "gray.500", _hover: { color: "blue.400" } };

  const copiedStyle =
    colorMode === "light"
      ? { color: "green.600", fontWeight: "bold" }
      : { color: "green.300" };

  const [showCopied, setShowCopied] = useState(false);

  const copyToClipboard = useCallback(() => {
    copy(text);
    setShowCopied(true);
  }, [text]);

  useEffect(() => {
    let timer;
    if (showCopied) {
      timer = setTimeout(() => {
        setShowCopied(false);
      }, 2500);
    }
    return () => {
      clearTimeout(timer);
    };
  }, [showCopied]);

  return (
    <Box position="relative" mt={2}>
      {/* Button for copy to clipboard */}
      <Box
        {...style}
        position="absolute"
        top="1"
        right="1"
        zIndex="1"
        fontSize={"xs"}
        onClick={copyToClipboard}
        cursor="pointer"
      >
        {showCopied ? (
          <Text {...copiedStyle}>
            <FontAwesomeIcon icon={faCheck} /> copied!
          </Text>
        ) : (
          <>
            <FontAwesomeIcon icon={faClipboard} /> copy
          </>
        )}
      </Box>

      {/* Code highlighter */}
      <SyntaxHighlighter style={syntaxTheme} wrapLines={true}>
        {text}
      </SyntaxHighlighter>
    </Box>
  );
};
