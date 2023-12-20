import React from "react";
import { clear_editor } from "utils/slate";
import { useSendInput as useAPISendInput } from "chat/hooks/useSendInput";

export const useSendInput = (chat, editor, highlights) => {
  const { sendInput: apiSendInput, error, loading } = useAPISendInput(chat.id);

  const sendInput = React.useCallback(async () => {
    const serializers = {};
    highlights.forEach((highlight) => {
      serializers[highlight.type] = highlight.serialize;
    });

    const { text: input, artifact_ids } = serialize(
      editor.children,
      serializers
    );
    if (input === "") {
      return;
    }

    // send input and then clear the input
    await apiSendInput(input, artifact_ids);
    clear_editor(editor);
  }, [editor, sendInput]);

  return { sendInput };
};

const default_serializer = (child) => {
  return child.text;
};

const serialize = (paragraphs, serializers) => {
  // serialize editor content to string.
  const artifact_ids = [];
  const serialized = paragraphs
    // Return the string content of each paragraph in the value's children.
    .map((paragraph) =>
      paragraph.children
        .map((child) => {
          // format nodes based on type
          const serializeFunc = serializers[child.type] || default_serializer;
          if (child.type === "artifact") {
            artifact_ids.push(child.object.id);
          }
          return serializeFunc(child);
        })
        .join("")
    )
    // Join them all with line breaks denoting paragraphs.
    .join("\n");
  return {
    text: serialized,
    artifact_ids,
  };
};
