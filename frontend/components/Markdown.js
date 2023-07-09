import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Box } from "@chakra-ui/react";
import styles from "./style.css";
import SyntaxHighlighter from "react-syntax-highlighter";
import {
  stackoverflowDark,
  stackoverflowLight,
} from "react-syntax-highlighter/dist/cjs/styles/hljs";
import { useChatColorMode } from "chains/editor/useColorMode";

const MarkDown = ({ content }) => {
  const { isLight } = useChatColorMode();
  const syntaxTheme = isLight ? stackoverflowLight : stackoverflowDark;
  const bg = isLight ? "rgba(0, 0, 0, 0.1)" : "rgba(0, 0, 0, 0.2)";
  return (
    <Box className="markdown">
      <ReactMarkdown
        children={content}
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            return !inline && match ? (
              <SyntaxHighlighter
                {...props}
                children={String(children).replace(/\n$/, "")}
                style={syntaxTheme}
                language={match[1]}
                PreTag="div"
              />
            ) : (
              <code
                {...props}
                className={className}
                style={{ backgroundColor: bg, paddingLeft: 3, paddingRight: 3 }}
              >
                {children}
              </code>
            );
          },
        }}
      />
    </Box>
  );
};

export default MarkDown;
