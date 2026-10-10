import React, { useMemo } from "react";
import { Slate, Editable, withReact } from "slate-react";
import { createEditor, Text } from "slate";
import lowlight from "lowlight";
import json from "highlight.js/lib/languages/json";
import { Box } from "@chakra-ui/react";
import "highlight.js/styles/github.css";

// Register JSON language
lowlight.registerLanguage("json", json);

const JSONEditor = ({ value, onChange }) => {
  const editor = useMemo(() => withReact(createEditor()), []);

  // Decorator function
  function decorate([node, path]) {
    if (!Text.isText(node)) {
      return [];
    }

    let parseResult;
    try {
      parseResult = lowlight.highlight("json", node.text, true);
    } catch (error) {
      return [];
    }

    const ranges = [];
    let start = 0;

    parseResult.value.forEach(({ value, type }) => {
      if (typeof value === "string") {
        const end = start + value.length;
        ranges.push({
          highlight: true,
          className: type ? `lowlight ${type}` : undefined,
          anchor: { path, offset: start },
          focus: { path, offset: end },
        });
        start = end;
      }
    });

    return ranges;
  }

  // Render Leaf function
  const renderLeaf = ({ attributes, children, leaf }) => {
    if (leaf.className) {
      children = (
        <span className={`highlight ${leaf.className}`}>{children}</span>
      );
    }

    return <span {...attributes}>{children}</span>;
  };

  return (
    <Box padding="5" borderWidth="1px" borderRadius="lg" bg={"gray.900"}>
      <Slate editor={editor} value={value} onChange={onChange}>
        <Editable renderLeaf={renderLeaf} decorate={decorate} />
      </Slate>
    </Box>
  );
};

export default JSONEditor;
