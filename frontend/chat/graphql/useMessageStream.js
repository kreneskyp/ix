import React, { useEffect, useState, useCallback } from "react";
import { fetchQuery, useRelayEnvironment } from "react-relay/hooks";
import { useChatMessageSubscription } from "chat/graphql/useChatMessageSubscription";
import { TaskLogMessagesQuery } from "task_log/graphql/TaskLogMessagesQuery";
import { findIndexFromEnd } from "utils/array";

/**
 * useMessageStream is a custom hook that manages the message stream for a chat.
 * It fetches the initial messages, sets up a subscription for new messages,
 * and groups the messages by their parent.
 *
 * @param {Object} chat - The chat object containing the chat id and related task.
 * @returns {Object} - An object containing the messages, setMessages function, and subscriptionActive flag.
 */
export const useMessageStream = (chat) => {
  const environment = useRelayEnvironment();

  // setup messages and handler
  const [messages, setMessages] = useState([]);

  // Handle incoming new messages and update message groups
  const handleNewMessage = useCallback((newMessage) => {
    setMessages((prevMessages) => {
      const parentID = newMessage.parent?.id || newMessage.id;
      const parentIndex = findIndexFromEnd(
        prevMessages,
        (group) => group.id === parentID
      );

      if (parentIndex !== -1) {
        return prevMessages.map((group, index) =>
          index === parentIndex
            ? { ...group, messages: [...group.messages, newMessage] }
            : group
        );
      } else {
        return [...prevMessages, { id: parentID, messages: [newMessage] }];
      }
    });
  }, []);

  // subscribe to messages
  const subscriptionActive = useChatMessageSubscription(
    chat.id,
    handleNewMessage
  );

  // Load initial messages synchronously
  useEffect(() => {
    const fetchData = async () => {
      const data = await fetchQuery(environment, TaskLogMessagesQuery, {
        taskId: chat.task.id,
      }).toPromise();

      // Roll up messages into groups
      const rolledUpMessages = data.taskLogMessages.reduce((acc, message) => {
        const parentID = message.parent?.id || message.id;
        const parentIndex = findIndexFromEnd(
          acc,
          (group) => group.id === parentID
        );

        if (parentIndex !== -1) {
          return acc.map((group, index) =>
            index === parentIndex
              ? { ...group, messages: [...group.messages, message] }
              : group
          );
        } else {
          return [...acc, { id: parentID, messages: [message] }];
        }
      }, []);

      setMessages(rolledUpMessages);
    };
    fetchData();
  }, [environment, chat.id]);

  return { messages, setMessages, subscriptionActive };
};
