import React from "react";
import { Box } from "@chakra-ui/react";
import { Text, createEditor } from "slate";
import { withHistory } from "slate-history";
import { Slate, Editable, withReact } from "slate-react";
import { useEditorColorMode } from "chains/editor/useColorMode";

const VARIABLE_PATTERN = /({\w+})/g;

/**
 * extract unformatted text from Slate js nodes
 */
function extractPlainText(nodes) {
  return nodes
    .map((n) => {
      if (n.text) return n.text;
      if (n.children) return extractPlainText(n.children) + "\n";
      return "";
    })
    .join("");
}

/**
 * Tokenize input into a list of strings and patterns to highlight.
 */
function tokenize(text) {
  let tokens = [];
  let lastIndex = 0;
  let match;

  while ((match = VARIABLE_PATTERN.exec(text)) !== null) {
    const [matchString] = match;
    const index = match.index;

    // Push the string before the match, if any
    if (index > lastIndex) {
      tokens.push(text.slice(lastIndex, index));
    }

    // Push the matched variable as an object token
    tokens.push({
      type: "variable",
      content: matchString,
    });

    lastIndex = index + matchString.length;
  }

  // If there's any remaining text after the last match, push it as a string
  if (lastIndex < text.length) {
    tokens.push(text.slice(lastIndex));
  }

  return tokens;
}

export const PromptMessageInput = ({ initialValue, onChange, ...props }) => {
  const editor = React.useMemo(
    () => withHistory(withReact(createEditor())),
    []
  );

  const [value, setValue] = React.useState([
    {
      children: [{ text: initialValue }],
    },
  ]);

  const previousPlainText = React.useRef(extractPlainText(value));

  const handleChange = React.useCallback(
    (newValue) => {
      const newPlainText = extractPlainText(newValue);

      // Only call onChange if the text has actually changed
      if (newPlainText !== previousPlainText.current) {
        if (onChange !== undefined) {
          onChange(newPlainText);
        }
        previousPlainText.current = newPlainText;
      }

      setValue(newValue);
    },
    [onChange]
  );

  const decorate = React.useCallback(([node, path]) => {
    const ranges = [];

    if (!Text.isText(node)) {
      return ranges;
    }

    const getLength = (token) => {
      if (typeof token === "string") {
        return token.length;
      } else if (typeof token.content === "string") {
        return token.content.length;
      } else {
        return token.content.reduce((l, t) => l + getLength(t), 0);
      }
    };

    const tokens = tokenize(node.text);
    let start = 0;

    for (const token of tokens) {
      const length = getLength(token);
      const end = start + length;

      if (typeof token !== "string") {
        ranges.push({
          [token.type]: true,
          anchor: { path, offset: start },
          focus: { path, offset: end },
        });
      }

      start = end;
    }

    return ranges;
  }, []);

  return (
    <Box {...props}>
      <Slate editor={editor} value={value} onChange={handleChange}>
        <Editable
          renderLeaf={(props) => <Leaf {...props} />}
          decorate={decorate}
        />
      </Slate>
    </Box>
  );
};

const Leaf = ({ attributes, children, leaf }) => {
  const { isLight } = useEditorColorMode();
  const color = isLight ? "blue.600" : "blue.400";
  const VARIABLE_PATTERN = /({\w+}|\$\w+)/;
  if (VARIABLE_PATTERN.test(leaf.text)) {
    return (
      <Box as={"span"} {...attributes} color={color}>
        {children}
      </Box>
    );
  }

  return <span {...attributes}>{children}</span>;
};
