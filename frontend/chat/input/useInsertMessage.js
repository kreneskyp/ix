import { useCallback } from "react";
import { Transforms, Editor } from "slate";

/**
 * Hook for inserting messages into the chat input
 * @returns {(function(*, *): void)|*}
 */
export const useInsertMessage = (editor) => {
  const insertMessage = useCallback(
    (message, type) => {
      if (!editor) return;

      const { selection } = editor;

      const messageNode = {
        type: type,
        character: message,
        children: [{ text: message }],
      };

      if (selection) {
        // Insert at the selection
        Transforms.insertNodes(editor, messageNode);
        Transforms.move(editor);
      } else {
        // Insert at the end of the document
        const endOfDoc = Editor.end(editor, []);
        Transforms.select(editor, endOfDoc);
        Transforms.insertNodes(editor, messageNode);
        Transforms.move(editor);
      }
    },
    [editor]
  );

  return insertMessage;
};
