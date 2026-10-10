import React, { useMemo } from "react";
import { Editor, createEditor } from "slate";
import { Slate, Editable, withReact } from "slate-react";
import { Box } from "@chakra-ui/react";
import { lowlight } from "lowlight";
import "lowlight/lib/all";

import { Fragment, jsx, jsxs } from "react/jsx-runtime";
import { renderToStaticMarkup } from "react-dom/server";
import { h } from "hastscript";

const CodeHighlightingEditor = () => {
  const editor = useMemo(() => withReact(createEditor()), []);

  const renderLeaf = ({ attributes, children, leaf }) => {
    let className = leaf.className ? leaf.className.join(" ") : "";
    return (
      <span {...attributes} className={className}>
        {children}
      </span>
    );
  };

  const decorate = ([node, path]) => {
    if (!Editor.isBlock(editor, node)) {
      const parent = Editor.parent(editor, path);
      if (parent[0].type === "code") {
        const lang = parent[0].language;
        const code = node.text;
        const tree = lowlight.highlight(lang || "json", code);
        const html = toH((name, props, ...children) => {
          return { text: children.join(""), className: props.className };
        }, tree);

        return html.map((node, i) => {
          const { text, ...rest } = node;
          return {
            ...rest,
            anchor: { path, offset: i },
            focus: { path, offset: i + text.length },
          };
        });
      }
    }

    return [];
  };

  return (
    <Box p={4} bg="gray.700" color="white">
      <Slate
        editor={editor}
        value={initialValue}
        onChange={(value) => setValue(value)}
      >
        <Editable renderLeaf={renderLeaf} decorate={decorate} />
      </Slate>
    </Box>
  );
};

export default CodeHighlightingEditor;
