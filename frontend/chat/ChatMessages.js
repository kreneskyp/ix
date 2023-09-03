import React, { useEffect, useRef } from "react";
import { Box } from "@chakra-ui/react";
import ChatMessage from "chat/ChatMessage";
import { useMessagesContext } from "chat/hooks/useChatMessageSubscription";
import { useMessagesTokenContext } from "chat/hooks/useChatMessageTokenSubscription";
import { useChatStyle } from "chat/ChatInterface";

export const ChatMessages = () => {
  const messages = useMessagesContext();
  const streams = useMessagesTokenContext();
  const messagesEndRef = useRef(null);
  const chatStyle = useChatStyle();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages, streams]);

  return (
    <Box height={"100%"} {...chatStyle.messages}>
      {messages.map((messageGroup) => (
        <ChatMessage key={messageGroup.id} messageGroup={messageGroup} />
      ))}
      <div ref={messagesEndRef} />
    </Box>
  );
};

export default ChatMessages;
