import React from "react";
import {
  Box,
  Flex,
  VStack,
  Text,
  Spinner,
  HStack,
} from "@chakra-ui/react";
import AssistantContent from "chat/AssistantContent";
import FeedbackContent from "chat/FeedbackContent";
import FeedbackRequestContent from "chat/FeedbackRequestContent";
import SystemContent from "chat/SystemContent";
import ChatMessageAvatar from "chat/ChatMessageAvatar";
import AutonomousModeContent from "chat/AutonomousModeContent";
import AuthorizeContent from "chat/AuthorizeContent";
import AuthRequestContent from "chat/AuthRequestContent";
import ExecuteContent from "chat/ExecuteContent";
import { useColorMode } from "@chakra-ui/color-mode";
import ExecuteErrorContent from "chat/ExecuteErrorContent";
import { PlanContent } from "planner/PlanContent";
import CommandContent from "chat/CommandContent";

import { useMemo } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheck } from "@fortawesome/free-solid-svg-icons";

const useMessageGroup = (messageGroup) => {
  // build message structure out of a group of messages
  return useMemo(() => {
    let think = null;
    let thought = null;
    let authorizations = [];
    const messages = [];

    messageGroup.messages.forEach((message) => {
      if (message.content.type === "THINK" && !think) {
        think = message;
      } else if (message.content.type === "THOUGHT" && !thought) {
        thought = message;
      } else if (message.content.type === "AUTHORIZE") {
        authorizations.push(message);
      } else {
        messages.push(message);
      }
    });

    return { think, thought, messages, authorizations };
  }, [messageGroup]);
};

const ChatMessageContent = ({ message }) => {
  let contentComponent;
  const content = message.content;
  switch (content.type) {
    case "ASSISTANT":
      contentComponent = <AssistantContent content={content} />;
      break;
    case "AUTONOMOUS":
      contentComponent = <AutonomousModeContent content={content} />;
      break;
    case "AUTHORIZE":
      contentComponent = <AuthorizeContent content={content} />;
      break;
    case "AUTH_REQUEST":
      contentComponent = <AuthRequestContent content={content} />;
      break;
    case "COMMAND":
      contentComponent = <CommandContent content={content} />;
      break;
    case "EXECUTED":
      contentComponent = <ExecuteContent message={message} />;
      break;
    case "EXECUTE_ERROR":
      contentComponent = <ExecuteErrorContent content={content} />;
      break;
    case "FEEDBACK":
      contentComponent = <FeedbackContent content={content} />;
      break;
    case "FEEDBACK_REQUEST":
      contentComponent = <FeedbackRequestContent content={content} />;
      break;
    case "SYSTEM":
      contentComponent = <SystemContent content={content} />;
      break;
    case "ARTIFACT":
      contentComponent = <PlanContent message={message} />;
      break;
    default:
      contentComponent = <div>{content.message}</div>;
      break;
  }
  return contentComponent;
};

const ChatMessageAuthorizations = ({ authorizations }) => {
  const { colorMode } = useColorMode();
  if (authorizations.length === 0) {
    return null;
  }

  // for now just show that it was authorized
  return (
    <HStack spacing={1} fontSize="xs">
      <Text color="green.300">
        <FontAwesomeIcon icon={faCheck} />
      </Text>
      <Text color={colorMode === "light" ? "gray.800" : "gray.500"}>
        Authorized
      </Text>
    </HStack>
  );
};

const ChatMessageFooter = ({ groupedMessages }) => {
  const { colorMode } = useColorMode();
  const { thought, authorizations } = groupedMessages;

  return (
    <Flex
      width="100%"
      bg={colorMode === "light" ? "blackAlpha.50" : "blackAlpha.300"}
      px={3}
      pb={1}
      pt={2}
      justifyContent="space-between"
    >
      <ChatMessageAuthorizations authorizations={authorizations} />
      {thought !== null && (
        <Text
          fontSize="xs"
          color={colorMode === "light" ? "gray.800" : "gray.500"}
        >
          <b>Runtime:</b> {thought?.content.runtime?.toFixed(2)} seconds.
        </Text>
      )}
    </Flex>
  );
};

const ChatMessage = ({ messageGroup }) => {
  const { colorMode } = useColorMode();
  const groupedMessages = useMessageGroup(messageGroup);
  const { think, thought, messages } = groupedMessages;

  // Main message is either a THINK or a plain message that doesn't have a parent.
  // Most messages should have parent THINK but this provides a fallback so all
  // messages are still rendered.
  let message;
  if (think !== null) {
    message = think;
  } else if (messages.length) {
    message = messages[0];
  }

  // Message content or spinner if still thinking
  let content = null;
  if (messages.length === 0 && thought === null) {
    content = <Spinner />;
  } else {
    content = messages.map((message) => (
      <ChatMessageContent key={message.id} message={message} />
    ));
  }

  // Use agent name when available
  const alias = message?.content.agent || message.role;

  return (
    <Flex alignItems="flex-start" mb={6} align="center">
      <VStack mt={3} mr={3} width={100}>
        <ChatMessageAvatar message={message} />
        <Text
          color={colorMode === "light" ? "blackAlpha.800" : "whiteAlpha.400"}
          fontSize="xs"
          fontWeight="bold"
        >
          {alias.toLowerCase()}
        </Text>
      </VStack>
      <Flex
        bg={colorMode === "light" ? "gray.100" : "gray.700"}
        width="800px"
        borderRadius={8}
        border="1px solid"
        borderColor={colorMode === "light" ? "gray.300" : "gray.700"}
        minHeight={90}
        p={0}
        direction="column"
        justify="space-between"
      >
        <Box p={3} color={colorMode === "light" ? "black" : "gray.100"}>
          {content}
        </Box>
        <ChatMessageFooter groupedMessages={groupedMessages} />
      </Flex>
    </Flex>
  );
};

export default ChatMessage;
