import React, { useEffect, useState, useCallback } from "react";
import { fetchQuery, useRelayEnvironment } from "react-relay/hooks";
import { useChatMessageSubscription } from "chat/graphql/useChatMessageSubscription";
import { TaskLogMessagesQuery } from "chat/graphql/TaskLogMessagesQuery";
import { findIndexFromEnd } from "utils/array";
import { useChatMessageTokenSubscription } from "chat/graphql/useChatMessageTokenSubscription";
import {groupBy} from "graphql/jsutils/groupBy";

/**
 * Helper for adding a token to an array of tokens. Tokens are ordered, but
 * sometimes they arrive out of order. This function inserts the token at the
 * correct position in the array.
 */
function addToArray(array, pair) {
  // Clone the array for immutability
  let newArray = [...array];

  // Check if pair needs to be appended at the end
  if (newArray.length === 0 || pair[0] > newArray[newArray.length - 1][0]) {
    newArray.push(pair);
  } else {
    // Find the correct index to insert the pair
    let indexToInsert = newArray.findIndex((item) => item[0] > pair[0]);

    // Insert the pair at the correct position
    newArray.splice(indexToInsert, 0, pair);
  }

  return newArray;
}

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
  const [streams, setStreams] = useState({});

  // Handle incoming new messages and update message groups
  const handleNewMessage = useCallback((newMessage) => {
    // update messages
    setMessages((prevMessages) => {
      // find group using parent id.
      const parentID = newMessage.parent?.id || newMessage.id;
      const parentIndex = findIndexFromEnd(
        prevMessages,
        (group) => group.id === parentID
      );

      if (parentIndex !== -1) {
        // update the message if already existing (streaming, but done)
        // or append to the end of the group.
        return prevMessages.map((group, index) => {
          if (index === parentIndex) {
            const messageIndex = group.messages.findIndex((message) => message.id === newMessage.id);
            if (messageIndex !== -1) {
              // update existing message
              const updatedMessages = [...group.messages];
              updatedMessages[messageIndex] = newMessage;
              return {...group, messages: updatedMessages};
            }

            // new message, append to the end of the group
            return {...group, messages: [...group.messages, newMessage]};
          }

          // not the group we are looking for
          return group;
        });

      } else {
        // new message group
        return [...prevMessages, { id: parentID, messages: [newMessage] }];
      }
    });

    setStreams((prevStreams) => {
      // remove stream cache if complete message has arrived
      if (newMessage.content?.stream === false && prevStreams[newMessage.id] !== undefined) {
        const newStreams = {...prevStreams};
        delete newStreams[newMessage.id];
        return newStreams;
      }
      return prevStreams;
    });
  }, []);

  const handleToken = useCallback((msg) => {
    // add token to stream
    const token = [msg.index, msg.text];
    setStreams((prevStreams) => {
      const stream = prevStreams[msg.msgId];
      const updatedStream =
        stream === undefined ? [token] : addToArray(stream, token);
      return {
        ...prevStreams,
        [msg.msgId]: updatedStream,
      };
    });
  }, []);

  // subscribe to messages - this includes both complete messages and streamed messages.
  const subscriptionActive = useChatMessageSubscription(
    chat.id,
    handleNewMessage
  );

  // subscribe to message stream - this includes tokens for messages as they are generated.
  const tokenSubscriptionActive = useChatMessageTokenSubscription(
    chat.id,
    handleToken
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

  return { messages, setMessages, streams, subscriptionActive };
};
