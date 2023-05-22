import React from "react";
import { Box, Text } from "@chakra-ui/react";
import PropTypes from "prop-types";
import { useChatColorMode } from "chains/editor/useColorMode";

/**
 * HighlightText is a component that takes a string and returns a Chakra Text component with
 * @mentions and {artifacts} highlighted.
 */
const HighlightText = ({ content }) => {
  const { mention, artifact } = useChatColorMode();

  const formattedContent = React.useMemo(() => {
    // Match @mentions and {artifacts} and return an array of Chakra Text components
    return content.split(" ").map((word, idx) => {
      if (word.startsWith("@")) {
        // Word is a mention
        return (
          <Text as="span" color={mention} key={idx}>
            {word + " "}
          </Text>
        );
      } else if (word.startsWith("{") && word.endsWith("}")) {
        // Word is an artifact
        return (
          <Text as="span" color={artifact} key={idx}>
            {word + " "}
          </Text>
        );
      } else {
        return word + " ";
      }
    });
  }, [content]);

  return <Box>{formattedContent}</Box>;
};

HighlightText.propTypes = {
  content: PropTypes.string.isRequired,
};

export default HighlightText;
