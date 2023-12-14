import React, {
  useState,
  useEffect,
  createContext,
  useContext,
  useMemo,
} from "react";
import { graphql, requestSubscription } from "react-relay";
import environment from "relay-environment";

export const MessagesTokenContext = createContext();
export const TokenSubscriptionActiveContext = createContext();

export const useMessagesTokenContext = () => useContext(MessagesTokenContext);
export const useTokenSubscriptionContext = () =>
  useContext(TokenSubscriptionActiveContext);

const chatMessageTokenSubscription = graphql`
  subscription useChatMessageTokenSubscription($chatId: String!) {
    chatMessageTokenSubscription(chatId: $chatId) {
      msgId
      index
      text
    }
  }
`;

/**
 * Helper for fetching the stream content for a message. This method
 * caches the concatenated string of all tokens in the stream. If the
 * stream is not available, undefined is returned.
 *
 * @param message_id
 * @returns {unknown} concatenated string of all tokens in the stream
 */
export const useStreamContent = (message_id) => {
  const streams = useContext(MessagesTokenContext);
  const stream = streams[message_id];
  const content = useMemo(() => {
    if (stream === undefined) {
      return undefined;
    }

    // join messages together
    return stream.map((item) => item[1]).join("");
  }, [message_id, stream]);
  return content;
};

export function useChatMessageTokenSubscription(chatId, onToken) {
  const [connectionActive, setConnectionActive] = useState(false);

  useEffect(() => {
    let subscription;

    const connect = () => {
      setConnectionActive(true);
      subscription = requestSubscription(environment, {
        subscription: chatMessageTokenSubscription,
        variables: { chatId },
        updater: (store, data) => {
          onToken(data.chatMessageTokenSubscription);
        },
        onError: (error) => {
          console.error("An error occurred:", error);
          setConnectionActive(false);

          // Reconnect after a delay
          setTimeout(connect, 5000);
        },
      });
    };

    connect();

    return () => {
      if (subscription) {
        subscription.dispose();
      }
      setConnectionActive(false);
    };
  }, [onToken, chatId]);

  return connectionActive;
}
