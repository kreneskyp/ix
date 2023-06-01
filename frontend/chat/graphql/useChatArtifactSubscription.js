import React, { useState, useEffect, createContext, useContext } from "react";
import { graphql, requestSubscription } from "react-relay";
import environment from "relay-environment";

export const MessagesContext = createContext();
export const SubscriptionActiveContext = createContext();

export const useArtifactsContext = () => useContext(MessagesContext);
export const useSubscriptionActiveContext = () =>
  useContext(SubscriptionActiveContext);

const chatArtifactSubscription = graphql`
  subscription useChatArtifactSubscription($chatId: String!) {
    chatArtifactSubscription(chatId: $chatId) {
      artifact {
        id
        key
        artifactType
        name
        description
        storage
        createdAt
      }
    }
  }
`;

export function useChatArtifactSubscription(chatId, onNewMessage) {
  const [connectionActive, setConnectionActive] = useState(false);

  useEffect(() => {
    let subscription;

    const connect = () => {
      setConnectionActive(true);
      subscription = requestSubscription(environment, {
        subscription: chatArtifactSubscription,
        variables: { chatId },
        updater: (store, data) => {
          onNewMessage(data.chatArtifactSubscription.artifact);
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
