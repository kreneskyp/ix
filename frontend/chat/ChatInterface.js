import React, { createContext, Suspense } from "react";
import { Center, useColorModeValue } from "@chakra-ui/react";
import { ScrollableBox } from "site/ScrollableBox";
import { useMessageStream } from "chat/hooks/useMessageStream";
import ChatMessages from "chat/ChatMessages";

import {
  MessagesContext,
  SubscriptionActiveContext,
} from "chat/hooks/useChatMessageSubscription";
import ChatInput from "chat/input/ChatInput";
import { MessagesTokenContext } from "chat/hooks/useChatMessageTokenSubscription";

const SCROLLBOX = {
  height: "calc(100vh - 50px - 100px)",
  mt: 2,
  mb: 2,
};

const INPUT = {
  width: 720,
  transform: "translateX(25px)",
  m: 0,
};

export const DEFAULT_CHAT_DARK_STYLE = {
  container: {},
  avatar: {
    bg: "gray.700",
    color: "whiteAlpha.400",
    border: "2px solid",
    borderColor: "transparent",
    avatarColor: "gray.500",
  },
  scrollbox: {
    ...SCROLLBOX,
  },
  message: {
    container: {
      width: 800,
    },
    body: {
      bg: "gray.700",
      border: "1px solid",
      borderColor: "gray.700",
      borderRadius: 8,
      p: 0,
    },
    content: {
      color: "gray.100",
    },
    footer: {
      bg: "blackAlpha.300",
      color: "gray.500",
    },
  },
  input: {
    ...INPUT,
    bg: "gray.800",
    color: "gray.100",
    borderColor: "gray.600",
  },
  autocomplete: {
    bg: "gray.800",
    color: "gray.100",
    borderColor: "gray.700",
  },
};

export const DEFAULT_CHAT_LIGHT_STYLE = {
  avatar: {
    bg: "gray.200",
    color: "blackAlpha.800",
    border: "2px solid",
    borderColor: "gray.300",
    avatarColor: "gray.600",
  },
  scrollbox: {
    ...SCROLLBOX,
  },
  messages: {
    width: 800,
  },
  message: {
    container: {
      width: 800,
    },
    body: {
      bg: "white",
      border: "1px solid",
      borderColor: "gray.300",
      borderRadius: 8,
      p: 0,
    },
    content: {
      bg: "white",
      color: "black",
      borderRadius: 8,
    },
    footer: {
      bg: "blackAlpha.50",
      color: "gray.800",
    },
  },
  input: {
    ...INPUT,
    bg: "gray.50",
    color: "gray.900",
    borderColor: "gray.300",
  },
  autocomplete: {
    bg: "gray.100",
    color: "gray.900",
    borderColor: "gray.300",
  },
};

export const DEFAULT_CHAT_STYLE = {
  dark: DEFAULT_CHAT_DARK_STYLE,
  light: DEFAULT_CHAT_LIGHT_STYLE,
};

export const ChatStyle = createContext(DEFAULT_CHAT_STYLE);

export const useChatStyle = () => {
  const { light, dark } = React.useContext(ChatStyle);
  return useColorModeValue(light, dark);
};

/**
 * Packaged chat interface with messages and input. Includes websocket
 * connection management and message streaming.
 *
 * @param graph - chat graph from useChatGraph
 */
export const ChatInterface = ({ graph, inputPl }) => {
  const { messages, streams, subscriptionActive } = useMessageStream(
    graph.chat
  );
  const { scrollbox } = useChatStyle();

  return (
    <MessagesTokenContext.Provider value={streams}>
      <MessagesContext.Provider value={messages}>
        <SubscriptionActiveContext.Provider value={subscriptionActive}>
          <ScrollableBox {...scrollbox}>
            <Suspense>
              <ChatMessages chat={graph.chat} />
            </Suspense>
          </ScrollableBox>
          <Center w="100%" mb={5}>
            {/* Bottom aligned section */}
            <ChatInput chat={graph.chat} />
          </Center>
        </SubscriptionActiveContext.Provider>
      </MessagesContext.Provider>
    </MessagesTokenContext.Provider>
  );
};

ChatInterface.defaultProps = {
  inputPl: 95,
};
