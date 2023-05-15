import { useEffect } from "react";
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
  useEffect(() => {
    const subscription = requestSubscription(environment, {
      subscription: taskLogMessagesSubscription,
      variables: { chatId },
      updater: (store, data) => {
        // reconstruct the message object here since the proper nested
        // structure doesn't work since graphene doesn't do async FKs well
        const parentId = data.chatMessageSubscription.parentId;
        onNewMessage({
          ...data.chatMessageSubscription.taskLogMessage,
          agent: data.chatMessageSubscription.agent,
          parent: parentId === null ? null : { id: parentId },
        });
      },
      onError: (error) => console.error("An error occurred:", error),
    });

    return () => {
      subscription.dispose();
    };
  }, [onNewMessage]);
}
