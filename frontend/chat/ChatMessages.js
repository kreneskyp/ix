import React, { useEffect, useRef } from "react";
import { Box } from "@chakra-ui/react";
import ChatMessage from "chat/ChatMessage";
import { useMessagesContext } from "chat/hooks/useChatMessageSubscription";
import { useMessagesTokenContext } from "chat/hooks/useChatMessageTokenSubscription";

export const ChatMessages = () => {
  const messages = useMessagesContext();
  const streams = useMessagesTokenContext();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages, streams]);

  return (
    <Box pt={5}>
      {messages.map((messageGroup) => (
        <ChatMessage key={messageGroup.id} messageGroup={messageGroup} />
      ))}
      <div ref={messagesEndRef} />
    </Box>
  );
};

export default ChatMessages;
