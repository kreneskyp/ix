import React, { useEffect, useState, useCallback } from "react";
import { useRelayEnvironment } from "react-relay/hooks";
import { useChatMessageSubscription } from "chat/hooks/useChatMessageSubscription";
import { findIndexFromEnd } from "utils/array";
import { useChatMessageTokenSubscription } from "chat/hooks/useChatMessageTokenSubscription";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";

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
    // convert graphql message
    const msg = {
      ...newMessage,
      created_at: newMessage.createdAt,
    };

    // update messages
    setMessages((prevMessages) => {
      // find group using parent id.
      const parentID = msg.parent?.id || msg.id;
      const parentIndex = findIndexFromEnd(
        prevMessages,
        (group) => group.id === parentID
      );

      if (parentIndex !== -1) {
        // update the message if already existing (streaming, but done)
        // or append to the end of the group.
        return prevMessages.map((group, index) => {
          if (index === parentIndex) {
            const messageIndex = group.messages.findIndex(
              (message) => message.id === msg.id
            );
            if (messageIndex !== -1) {
              // update existing message
              const updatedMessages = [...group.messages];
              updatedMessages[messageIndex] = msg;
              return { ...group, messages: updatedMessages };
            }

            // new message, append to the end of the group
            return { ...group, messages: [...group.messages, msg] };
          }

          // not the group we are looking for
          return group;
        });
      } else {
        // new message group
        return [...prevMessages, { id: parentID, messages: [msg] }];
      }
    });

    setStreams((prevStreams) => {
      // remove stream cache if complete message has arrived
      if (msg.content?.stream === false && prevStreams[msg.id] !== undefined) {
        const newStreams = { ...prevStreams };
        delete newStreams[msg.id];
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

  const { page, load } = usePaginatedAPI(`/api/chats/${chat.id}/messages`, {
    limit: 100000,
    load: false,
  });

  // Load initial messages synchronously
  useEffect(() => {
    load();
  }, [chat.id]);

  useEffect(() => {
    if (!page) return;

    // Roll up messages into groups
    const rolledUpMessages = page?.objects.reduce((acc, message) => {
      const parentID = message.parent_id || message.id;
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

    if (rolledUpMessages) {
      setMessages(rolledUpMessages);
    }
  }, [page]);

  return { messages, setMessages, streams, subscriptionActive };
};
