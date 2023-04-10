import React from "react";
import { Box, Flex } from "@chakra-ui/react";
import PropTypes from "prop-types";
import AssistantContent from "chat/AssistantContent";
import UserFeedbackContent from "chat/UserFeedbackContent";
import FeedbackRequestContent from "chat/FeedbackRequestContent";
import SystemContent from "chat/SystemContent";
import ChatMessageAvatar from "chat/ChatMessageAvatar";

const ChatMessage = ({ message }) => {
  const { content } = message;

  let contentComponent = null;
  switch (content.type) {
    case "ASSISTANT":
      contentComponent = <AssistantContent content={content} />;
      break;
    case "FEEDBACK":
      contentComponent = <UserFeedbackContent content={content} />;
      break;
    case "FEEDBACK_REQUEST":
      contentComponent = <FeedbackRequestContent content={content} />;
      break;
    case "SYSTEM":
      contentComponent = <SystemContent content={content} />;
      break;
    default:
      contentComponent = <div>{content.message}</div>;
      break;
  }

  return (
    <Flex alignItems="flex-start" mb={4}>
      <Box mt={5} mr={3}>
        <ChatMessageAvatar message={message} />
      </Box>
      <Box bg="gray.100" borderRadius={8} p={3}>
        {contentComponent}
      </Box>
    </Flex>
  );
};

ChatMessage.propTypes = {
  message: PropTypes.shape({
    role: PropTypes.string.isRequired,
    content: PropTypes.any.isRequired,
  }).isRequired,
};

export default ChatMessage;
