import React, { useEffect, useRef } from "react";
import { Box } from "@chakra-ui/react";
import ChatMessage from "chat/ChatMessage";
import { useMessagesContext } from "chat/graphql/useChatMessageSubscription";

export const ChatMessages = () => {
  const messages = useMessagesContext();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  return (
    <Box>
      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </Box>
  );
};

export default ChatMessages;
