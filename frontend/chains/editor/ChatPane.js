import React, { useEffect } from "react";
import { Box, Spinner } from "@chakra-ui/react";
import { useChatGraph } from "chat/hooks/useChatGraph";
import {
  ChatInterface,
  ChatStyle,
  DEFAULT_CHAT_DARK_STYLE,
  DEFAULT_CHAT_LIGHT_STYLE,
  DEFAULT_CHAT_STYLE,
} from "chat/ChatInterface";

const SCROLLBOX = {
  height: "calc(100vh - 50px - 120px)",
  width: "100%",
};

const INPUT = {
  width: "calc(100% - 30px)",
};

const CHAT_PANE_DARK_STYLE = {
  ...DEFAULT_CHAT_DARK_STYLE,
  container: {},
  scrollbox: {
    ...DEFAULT_CHAT_STYLE.dark.scrollbox,
    ...SCROLLBOX,
  },
  avatar: {
    ...DEFAULT_CHAT_STYLE.dark.avatar,
    bg: "blackAlpha.400",
    border: "1px solid",
    borderColor: "transparent",
  },
  messages: {
    width: "100%",
  },
  message: {
    ...DEFAULT_CHAT_STYLE.dark.message,
    container: {},
    body: {},
    content: {
      ...DEFAULT_CHAT_STYLE.dark.message.content,
      bg: "blackAlpha.200",
      borderRadius: 5,
    },
    footer: {
      ...DEFAULT_CHAT_STYLE.dark.message.footer,
      bg: "transparent",
    },
  },
  input: {
    ...INPUT,
    bg: "gray.800",
    color: "gray.100",
    borderColor: "gray.600",
  },
};

const CHAT_PANE_LIGHT_STYLE = {
  ...DEFAULT_CHAT_LIGHT_STYLE,
  container: {},
  scrollbox: {
    ...DEFAULT_CHAT_STYLE.dark.scrollbox,
    ...SCROLLBOX,
  },
  avatar: {
    ...DEFAULT_CHAT_STYLE.light.avatar,
    color: "blackAlpha.800",
    bg: "gray.200",
    avatarColor: "gray.600",
  },
  messages: {
    width: "100%",
  },
  message: {
    ...DEFAULT_CHAT_STYLE.light.message,
    container: {},
    body: {},
    content: {
      ...DEFAULT_CHAT_STYLE.light.message.content,
      bg: "blackAlpha.200",
      borderRadius: 5,
    },
    footer: {
      ...DEFAULT_CHAT_STYLE.light.message.footer,
      bg: "transparent",
    },
  },
  input: {
    ...INPUT,
    bg: "gray.50",
    color: "gray.900",
    borderColor: "gray.300",
  },
};

// Custom theme for chat in pane in the sidebar.
const CHAT_PANE_STYLE = {
  dark: CHAT_PANE_DARK_STYLE,
  light: CHAT_PANE_LIGHT_STYLE,
};

export const ChatPane = () => {
  const { chain } = React.useContext(ChainState);
  const { id } = useTestChat(chain.id);
  const { response, call: loadGraph, isLoading } = useChatGraph(id);
  const graph = response?.data;

  useEffect(() => {
    loadGraph();
  }, [id]);

  return (
    <ChatStyle.Provider value={CHAT_PANE_STYLE}>
      {isLoading || !graph ? (
        <Spinner />
      ) : (
        <Box mt={3}>
          <ChatInterface graph={graph} />
        </Box>
      )}
    </ChatStyle.Provider>
  );
};
