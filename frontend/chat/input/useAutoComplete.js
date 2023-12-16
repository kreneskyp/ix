import React from "react";
import { Editor, Range } from "slate";

export const useAutoComplete = (editor) => {
  const [search, setSearch] = React.useState(null);
  const [type, setType] = React.useState(null);
  const [target, setTarget] = React.useState(null);
  const [selected, setSelected] = React.useState(0);

  // handler for editor changes
  const handleChange = React.useCallback(
    (newValue) => {
      const searchForHighlight = (editor, _type, pattern) => {
        const { selection } = editor;
        if (selection && Range.isCollapsed(selection)) {
          // before
          const [start] = Range.edges(selection);
          const wordBefore = Editor.before(editor, start, { unit: "word" });
          const before = wordBefore && Editor.before(editor, wordBefore);
          const beforeRange = before && Editor.range(editor, before, start);
          const beforeText = beforeRange && Editor.string(editor, beforeRange);

          // match
          const beforeMatch = beforeText && beforeText.match(pattern);

          // after
          const after = Editor.after(editor, start);
          const afterRange = Editor.range(editor, start, after);
          const afterText = Editor.string(editor, afterRange);
          const afterMatch = afterText.match(/^(\s|$)/);

          if (beforeMatch && afterMatch) {
            setTarget(beforeRange);
            setType(_type);
            setSearch(beforeMatch[1]);
            setSelected(0);
            return true;
          }
        }
        return false;
      };

      // search text for agent mentions
      if (searchForHighlight(editor, "mention", /^@(\w+)$/)) {
        return;
      }

      // search text for artifact mentions
      if (searchForHighlight(editor, "artifact", /^{(\w+)$/)) {
        return;
      }

      // no target was found after update, clear target.
      if (target !== null) {
        setTarget(null);
      }
    },
    [editor]
  );

  return {
    search,
    setSearch,
    target,
    setTarget,
    type,
    setType,
    selected,
    setSelected,
    handleChange,
  };
};
