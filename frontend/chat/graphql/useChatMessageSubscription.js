import { useState, useEffect } from "react";
import { graphql, requestSubscription } from "react-relay";
import environment from "relay-environment";

const taskLogMessagesSubscription = graphql`
  subscription useChatMessageSubscription($chatId: String!) {
    chatMessageSubscription(chatId: $chatId) {
      taskLogMessage {
        id
        role
        content
        createdAt
      }
      agent {
        id
        alias
      }
      parentId
    }
  }
`;

export function useChatMessageSubscription(chatId, onNewMessage) {
  const [connectionActive, setConnectionActive] = useState(false);

  useEffect(() => {
    let subscription;

    const connect = () => {
      subscription = requestSubscription(environment, {
        subscription: taskLogMessagesSubscription,
        variables: { chatId },
        updater: (store, data) => {
          const parentId = data.chatMessageSubscription.parentId;
          onNewMessage({
            ...data.chatMessageSubscription.taskLogMessage,
            agent: data.chatMessageSubscription.agent,
            parent: parentId === null ? null : { id: parentId },
          });
          setConnectionActive(true);
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
  }, [onNewMessage, chatId]);

  return connectionActive;
}
