import React, { useState, useEffect, useCallback } from "react";
import { Box } from "@chakra-ui/react";
import { fetchQuery, useRelayEnvironment } from "react-relay/hooks";
import { useChatMessageSubscription } from "chat/graphql/useChatMessageSubscription";
import { TaskLogMessagesQuery } from "task_log/graphql/TaskLogMessagesQuery";
import ChatMessage from "chat/ChatMessage";

export const ChatMessages = ({ chat }) => {
  const environment = useRelayEnvironment();
  const [messages, setMessages] = useState([]);

  // Load initial messages synchronously
  useEffect(() => {
    const fetchData = async () => {
      const data = await fetchQuery(environment, TaskLogMessagesQuery, {
        taskId: chat.task.id,
      }).toPromise();
      setMessages(data.taskLogMessages);
    };
    fetchData();
  }, [environment, chat.id]);

  const handleNewMessage = useCallback((newMessage) => {
    setMessages((prevMessages) => [...prevMessages, newMessage]);
  }, []);

  // Set up subscription to new messages
  useChatMessageSubscription(chat.id, handleNewMessage);

  return (
    <Box>
      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}
    </Box>
  );
};

export default ChatMessages;
