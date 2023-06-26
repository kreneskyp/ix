import React from "react";
import { Box, Text, Link, Code } from "@chakra-ui/react";
import PropTypes from "prop-types";
import { useChatColorMode } from "chains/editor/useColorMode";

/**
 * HighlightText is a component that takes a string and returns a Chakra Text component with
 * @mentions, {artifacts}, markdown URLs, and inline code references highlighted.
 */
const HighlightText = ({ content }) => {
  const { mention, artifact } = useChatColorMode();

  const formattedContent = React.useMemo(() => {
    return content.split(/(\s+)/).map((segment, idx) => {
      if (segment.startsWith("@")) {
        return (
          <Text as="span" sx={mention} key={idx}>
            {segment}
          </Text>
        );
      } else if (segment.startsWith("{") && segment.endsWith("}")) {
        return (
          <Text as="span" sx={artifact} key={idx}>
            {segment}
          </Text>
        );
      } else {
        const markdownLinkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
        const matchMarkdownLink = markdownLinkRegex.exec(segment);

        if (matchMarkdownLink) {
          const text = matchMarkdownLink[1];
          const url = matchMarkdownLink[2];

          return (
            <Link href={url} key={idx} isExternal color={"blue.400"}>
              {text}
            </Link>
          );
        } else {
          const codeRegex = /`([^`]+)`/g;
          const matchCode = codeRegex.exec(segment);

          if (matchCode) {
            const code = matchCode[1];

            return <Code key={idx}>{code}</Code>;
          }
        }

        return segment;
      }
    });
  }, [content, mention, artifact]);

  return <Box style={{ whiteSpace: "pre-wrap" }}>{formattedContent}</Box>;
};

HighlightText.propTypes = {
  content: PropTypes.string.isRequired,
};

export default HighlightText;
