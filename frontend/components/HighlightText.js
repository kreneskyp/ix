import React from "react";
import { Box, Text, Link, Code } from "@chakra-ui/react";
import PropTypes from "prop-types";

import { useChatColorMode } from "chains/editor/useColorMode";
import { HighlightedCode } from "components/HighlightedCode";

/**
 * HighlightText is a component that takes a string and returns a Chakra Text component with
 * @mentions, {artifacts}, markdown URLs, and inline code references highlighted.
 */
const HighlightText = ({ content }) => {
  const { mention, artifact } = useChatColorMode();

  const regexComponentPairs = React.useMemo(
    () => [
      {
        regex: /@\w+/g,
        component: (match, idx) => (
          <Text as="span" sx={mention} key={idx}>
            {match}
          </Text>
        ),
      },
      {
        regex: /\{[^\}]+\}/g,
        component: (match, idx) => (
          <Text as="span" sx={artifact} key={idx}>
            {match}
          </Text>
        ),
      },
      {
        regex: /\*\*([^*]+)\*\*/g,
        component: (match, idx, execResult) => (
          <strong key={idx}>{execResult[1]}</strong>
        ),
      }, // Markdown Bold
      {
        regex: /\[([^\]]+)\]\(([^)]+)\)/g,
        component: (match, idx, execResult) => (
          <Link href={execResult[2]} key={idx} isExternal color={"blue.400"}>
            {execResult[1]}
          </Link>
        ),
      },
      {
        regex: /```([\w\s]*?)\n([\s\S]*?)(```|$)/g,
        component: (match, idx, execResult) => {
          // execResult[2] contains the actual code content
          const codeText = execResult[2].replace(/\s+$/, "");
          return <HighlightedCode text={codeText} />;
        },
      },
      {
        regex: /`([^`]+)`/g,
        component: (match, idx, execResult) => (
          <Code key={idx}>{execResult[1]}</Code>
        ),
      },
    ],
    [mention, artifact]
  );

  const formattedContent = React.useMemo(() => {
    if (content === undefined) {
      return <div>"no content field"</div>;
    }

    let segments = [content];
    let key = 0;

    regexComponentPairs.forEach(({ regex, component }) => {
      let newSegments = [];
      segments.forEach((segment) => {
        if (typeof segment === "string") {;
          let lastIndex = 0;
          let match;
          regex.lastIndex = 0; // Reset lastIndex due to the 'g' flag

          while ((match = regex.exec(segment)) !== null) {
            const matchedText = match[0];
            const prefix = segment.substring(lastIndex, match.index);
            lastIndex = regex.lastIndex;

            if (prefix) newSegments.push(prefix);
            newSegments.push(component(matchedText, key++, match));
          }

          const postfix = segment.substring(lastIndex);
          if (postfix) newSegments.push(postfix);
        } else {
          newSegments.push(segment);
        }
      });
      segments = newSegments;
    });

    return segments;
  }, [content, regexComponentPairs]);

  return <Box style={{ whiteSpace: "pre-wrap" }}>{formattedContent}</Box>;
};

HighlightText.propTypes = {
  content: PropTypes.string.isRequired,
};

export default HighlightText;
