import React, { useCallback } from "react";
import { ChatInputContext } from "chat/input/ChatInputContext";
import { MentionElement } from "chat/input/MentionElement";
import { ArtifactElement } from "chat/input/ArtifactElement";
import { useChatInputEditor } from "chat/input/useChatInputEditor";
import { useInsertMessage } from "chat/input/useInsertMessage";
import { useAutoComplete } from "chat/input/useAutoComplete";
import { Leaf } from "chat/input/Leaf";
import { Element } from "chat/input/Element";

const DEFAULT_HIGHLIGHTS = [
  {
    type: "mention",
    autocomplete: /^@(\w+)$/,
    serialize: (child) => `@${child.display}`,
    element: MentionElement,
  },
  {
    type: "artifact",
    autocomplete: /^{(\w+)$/,
    serialize: (child) => `{${child.display}}`,
    element: ArtifactElement,
  },
];

const DEFAULT_CONFIG = {
  highlights: DEFAULT_HIGHLIGHTS,
};

export const ChatInputProvider = ({ config, children }) => {
  const { editor } = useChatInputEditor(config);
  const { insertMessage } = useInsertMessage(editor);
  const autoComplete = useAutoComplete(editor);

  const renderProps = {
    renderElement: useCallback(
      (props) => <Element {...props} highlights={config.highlights} />,
      []
    ),
    renderLeaf: useCallback((props) => <Leaf {...props} />, []),
  };

  const value = {
    editor,
    config,
    insertMessage,
    autoComplete,
    renderProps,
  };

  return (
    <ChatInputContext.Provider value={value}>
      {children}
    </ChatInputContext.Provider>
  );
};

ChatInputProvider.defaultProps = {
  config: DEFAULT_CONFIG,
};
