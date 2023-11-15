import React, { useState } from "react";
import { createEditor } from "slate";
import { withHistory } from "slate-history";
import { withReact } from "slate-react";

export const useChatInputEditor = (config) => {
  const [editor] = useState(() =>
    withHighlights(withReact(withHistory(createEditor())), config)
  );

  return { editor };
};

const withHighlights = (editor, config) => {
  const { isInline, isVoid, markableVoid } = editor;

  const highlight_keys = config.highlights.map((highlight) => highlight.type);
  const isHighlight = (element) => highlight_keys.includes(element.type);

  editor.isInline = (element) => {
    return isHighlight(element) ? true : isInline(element);
  };

  editor.isVoid = (element) => {
    return isHighlight(element) ? true : isVoid(element);
  };

  editor.markableVoid = (element) => {
    return isHighlight(element) || markableVoid(element);
  };

  return editor;
};
