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
    return content.split(/(\s|\n)/).map((segment, idx) => {
      if (segment.startsWith("@")) {
        return (
          <Text as="span" color={mention} key={idx}>
            {segment}
          </Text>
        );
      } else if (segment.startsWith("{") && segment.endsWith("}")) {
        return (
          <Text as="span" color={artifact} key={idx}>
            {segment}
          </Text>
        );
      } else if (segment === "\n") {
        return <br key={idx} />;
      } else {
        return segment;
      }
    });
  }, [content, mention, artifact]);

  return <Box>{formattedContent}</Box>;
};

HighlightText.propTypes = {
  content: PropTypes.string.isRequired,
};

export default HighlightText;
