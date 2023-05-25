export const clear_editor = (editor) => {
  // clear editor, removing all text, history, and selection
  const point = { path: [0, 0], offset: 0 };
  editor.selection = { anchor: point, focus: point };
  editor.history = { redos: [], undos: [] };
  editor.children = [
    {
      type: "paragraph",
      children: [{ text: "" }],
    },
  ];
};

// slate editor requires at least this minimum content for an empty editor
export const INITIAL_EDITOR_CONTENT = [
  {
    type: "paragraph",
    children: [{ text: "" }],
  },
];
