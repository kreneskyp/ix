import Prism from "prismjs";
import "prismjs/components/prism-javascript";
import "prismjs/components/prism-jsx";
import "prismjs/components/prism-typescript";
import "prismjs/components/prism-tsx";
import "prismjs/components/prism-markdown";
import "prismjs/components/prism-python";
import "prismjs/components/prism-json";
import React, { useCallback, useState } from "react";
import { createEditor, Node, Editor, Range, Element, Transforms } from "slate";
import {
  withReact,
  Slate,
  Editable,
  ReactEditor,
  useSlateStatic,
  useSlate,
} from "slate-react";
import { withHistory } from "slate-history";
import isHotkey from "is-hotkey";

import { Box, HStack } from "@chakra-ui/react";
import { normalizeTokens } from "components/code_editor/normalize-tokens";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { LineNumbers } from "components/code_editor/LineNumbers";
import { CODE_EDITOR_THEME_DARK } from "components/code_editor/theme-dark";
import { CODE_EDITOR_THEME_LIGHT } from "components/code_editor/theme-light";

const ParagraphType = "paragraph";
const CodeBlockType = "code-block";
const CodeLineType = "code-line";

function extractPlainText(nodes) {
  return nodes
    .map((n) => {
      if (n.text) return n.text;
      if (n.children) return extractPlainText(n.children) + "\n";
      return "";
    })
    .join("");
}

export const CodeEditor = ({ value, language, onChange }) => {
  const style = useEditorColorMode();
  const [editor] = useState(() => withHistory(withReact(createEditor())));
  const _value = value || "";

  const decorate = useDecorate(editor);
  const onKeyDown = useOnKeydown(editor);

  const input_style = {
    border: "1px solid",
    borderColor: "gray.700",
    borderRadius: 5,
  };

  // Value is encoded to a single code block element to ensure that
  // there is exactly one eternal CodeBlockType element in the editor.
  const encodedValue = React.useMemo(
    () => [
      {
        type: CodeBlockType,
        language: language,
        children: toCodeLines(_value),
      },
    ],
    [_value]
  );

  const handleChange = React.useCallback(
    (newValue) => {
      const newPlainText = extractPlainText(newValue);
      if (newPlainText !== _value) {
        if (onChange !== undefined) {
          onChange(newPlainText);
        }
      }
    },
    [onChange]
  );

  return (
    <Box
      h={"100%"}
      w={"100%"}
      {...input_style}
      {...style.input}
      maxHeight={"500px"}
      overflowY={"auto"}
      css={style.scrollbar}
    >
      <Slate
        editor={editor}
        value={encodedValue}
        onChange={onChange ? handleChange : undefined}
      >
        <SetNodeToDecorations />
        <HStack spacing={0}>
          <LineNumbers />
          <Box py={2} w={"100%"}>
            <Editable
              decorate={decorate}
              renderElement={(props) => ElementWrapper(props, language)}
              renderLeaf={renderLeaf}
              onKeyDown={onKeyDown}
            />
          </Box>
        </HStack>

        <style>
          {style.isLight ? CODE_EDITOR_THEME_LIGHT : CODE_EDITOR_THEME_DARK}
        </style>
      </Slate>
    </Box>
  );
};

const ElementWrapper = (props, language) => {
  const { attributes, children, element } = props;
  const editor = useSlateStatic();

  if (element.type === CodeBlockType) {
    Transforms.setNodes(
      editor,
      { language },
      { at: ReactEditor.findPath(editor, element) }
    );

    return (
      <Box
        {...attributes}
        cx={{
          position: "relative",
          fontFamily: "monospace",
          marginTop: 0,
          padding: "5px 13px",
        }}
        ml={2}
        fontSize={"sm"}
        style={{ position: "relative" }}
        spellCheck={false}
      >
        {children}
      </Box>
    );
  }

  if (element.type === CodeLineType) {
    return (
      <Box {...attributes} style={{ position: "relative" }}>
        {children}
      </Box>
    );
  }

  const Tag = editor.isInline(element) ? "span" : "div";
  return (
    <Tag {...attributes} style={{ position: "relative" }}>
      {children}
    </Tag>
  );
};

const renderLeaf = (props) => {
  const { attributes, children, leaf } = props;
  return (
    <span
      {...attributes}
      className={Object.keys(leaf)
        .filter((key) => key !== "text")
        .join(" ")}
    >
      {children}
    </span>
  );
};

const useDecorate = (editor) => {
  return useCallback(
    ([node, path]) => {
      if (Element.isElement(node) && node.type === CodeLineType) {
        const ranges = editor.nodeToDecorations.get(node) || [];
        return ranges;
      }
      return [];
    },
    [editor.nodeToDecorations]
  );
};

const getChildNodeToDecorations = ([block, blockPath]) => {
  const nodeToDecorations = new Map();

  const text = block.children.map((line) => Node.string(line)).join("\n");
  const language = block.language;
  const tokens = Prism.tokenize(text, Prism.languages[language]);
  const normalizedTokens = normalizeTokens(tokens); // Ensure this utility function is defined
  const blockChildren = block.children;

  for (let index = 0; index < normalizedTokens.length; index++) {
    const tokens = normalizedTokens[index];
    const element = blockChildren[index];

    if (!nodeToDecorations.has(element)) {
      nodeToDecorations.set(element, []);
    }

    let start = 0;
    for (const token of tokens) {
      const length = token.content.length;
      if (!length) {
        continue;
      }

      const end = start + length;
      const path = [...blockPath, index, 0];
      const range = {
        anchor: { path, offset: start },
        focus: { path, offset: end },
        token: true,
        ...Object.fromEntries(token.types.map((type) => [type, true])),
      };

      nodeToDecorations.get(element).push(range);
      start = end;
    }
  }

  return nodeToDecorations;
};

const SetNodeToDecorations = () => {
  const editor = useSlate();

  const blockEntries = Array.from(
    Editor.nodes(editor, {
      at: [],
      mode: "highest",
      match: (n) => Element.isElement(n) && n.type === CodeBlockType,
    })
  );

  const nodeToDecorations = mergeMaps(
    ...blockEntries.map(getChildNodeToDecorations)
  );
  editor.nodeToDecorations = nodeToDecorations;

  return null;
};

const useOnKeydown = (editor) => {
  const onKeyDown = useCallback(
    (e) => {
      if (isHotkey("tab", e)) {
        e.preventDefault();
        Editor.insertText(editor, "  ");
      }
    },
    [editor]
  );

  return onKeyDown;
};

const mergeMaps = (...maps) => {
  const map = new Map();

  for (const m of maps) {
    for (const [key, value] of m) {
      map.set(key, value);
    }
  }

  return map;
};

const toChildren = (content) => [{ text: content }];

const toCodeLines = (content) => {
  const split = content?.split("\n") || [""];

  // build lines:
  return split.map((line, i) => ({
    type: CodeLineType,
    children: toChildren(line),
    line: i,
  }));
};

export default CodeEditor;
