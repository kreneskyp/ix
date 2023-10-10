import React from "react";
import { Box, Flex, VStack, Text, HStack } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import { useMemo } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faArrowUpRightFromSquare,
  faCheck,
} from "@fortawesome/free-solid-svg-icons";

import ChatMessageAvatar from "chat/messages/ChatMessageAvatar";
import AssistantContent from "chat/messages/AssistantContent";
import FeedbackContent from "chat/messages/FeedbackContent";
import FeedbackRequestContent from "chat/messages/FeedbackRequestContent";
import SystemContent from "chat/messages/SystemContent";
import AutonomousModeContent from "chat/messages/AutonomousModeContent";
import AuthorizeContent from "chat/messages/AuthorizeContent";
import AuthRequestContent from "chat/messages/AuthRequestContent";
import ExecuteContent from "chat/messages/ExecuteContent";
import ExecuteErrorContent from "chat/messages/ExecuteErrorContent";
import CommandContent from "chat/messages/CommandContent";
import { ArtifactContent } from "chat/messages/ArtifactContent";
import HighlightText from "components/HighlightText";
import { useChatStyle } from "chat/ChatInterface";

const useMessageGroup = (messageGroup) => {
  // build message structure out of a group of messages
  return useMemo(() => {
    let think = null;
    let thought = null;
    let authorizations = [];
    let errors = [];
    const messages = [];

    messageGroup.messages.forEach((message) => {
      if (message.content.type === "THINK" && !think) {
        think = message;
      } else if (message.content.type === "THOUGHT" && !thought) {
        thought = message;
      } else if (message.content.type === "AUTHORIZE") {
        authorizations.push(message);
      } else if (message.content.type === "EXECUTE_ERROR") {
        errors.push(message);
        messages.push(message);
      } else {
        messages.push(message);
      }
    });

    return { think, thought, messages, authorizations, errors };
  }, [messageGroup]);
};

const ChatMessageContent = ({ message }) => {
  let contentComponent;
  const content = message.content;
  switch (content.type) {
    case "ASSISTANT":
      contentComponent = <AssistantContent message={message} />;
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
      contentComponent = <ArtifactContent message={message} />;
      break;
    case "THOUGHT":
      contentComponent = null;
      break;
    default:
      contentComponent = <HighlightText content={content.message} />;
      break;
  }
  return contentComponent;
};

const ChatMessageAuthorizations = ({ authorizations }) => {
  const { colorMode } = useColorMode();
  if (authorizations.length === 0) {
    return <Text></Text>;
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

const LangSmithLink = ({ thought }) => {
  const { colorMode } = useColorMode();
  if (thought?.content?.run_id === undefined || !thought?.content?.langsmith) {
    return null;
  }

  return (
    <Text
      fontSize="xs"
      color={colorMode === "light" ? "gray.800" : "gray.500"}
      as={"span"}
    >
      <a target="_langsmith" href={`/langsmith/${thought.content.run_id}/`}>
        <b>LangSmith</b> <FontAwesomeIcon icon={faArrowUpRightFromSquare} />
      </a>
    </Text>
  );
};

const ChatMessageFooter = ({ groupedMessages }) => {
  const { thought, authorizations } = groupedMessages;
  const chatStyle = useChatStyle();

  return (
    <Flex
      width="100%"
      px={3}
      pb={1}
      pt={2}
      {...chatStyle.message.footer}
      justifyContent="space-between"
    >
      <ChatMessageAuthorizations authorizations={authorizations} />
      {thought !== null && (
        <Text fontSize="xs" color={chatStyle.message.footer.color}>
          <b>Runtime:</b> {thought?.content.runtime?.toFixed(2)} seconds.{" "}
          <LangSmithLink thought={thought} />
        </Text>
      )}
    </Flex>
  );
};

const ChatMessage = ({ messageGroup }) => {
  const groupedMessages = useMessageGroup(messageGroup);
  const { think, thought, messages, errors } = groupedMessages;
  const chatStyle = useChatStyle();

  // Main message is either a THINK or a plain message that doesn't have a parent.
  // Most messages should have parent THINK but this provides a fallback so all
  // messages are still rendered.
  let message;
  if (think !== null) {
    message = think;
  } else if (messages.length) {
    message = messages[0];
  }

  const isThinking = think !== null && thought === null && !errors.length;

  // Message content or spinner if still thinking
  let content = null;
  if (messages.length === 0 && thought === null) {
    content = null;
  } else {
    content = messages.map((message) => (
      <ChatMessageContent key={message.id} message={message} />
    ));
  }

  // Use agent name when available
  const alias = message?.content.agent || message?.role || "Unknown";

  return (
    <Flex
      alignItems="flex-start"
      mb={0}
      mx={0}
      align="center"
      borderTop={"0px solid"}
      borderColor={"whiteAlpha.200"}
      pt={3}
      {...chatStyle.message.container}
    >
      <VStack mt={0} mr={2}>
        <ChatMessageAvatar message={message} isThinking={isThinking} />
        <Text color={chatStyle.avatar.color} fontSize="xs" fontWeight="bold">
          {alias.toLowerCase()}
        </Text>
      </VStack>
      <Flex
        width="100%"
        minHeight={90}
        direction="column"
        justify="space-between"
        {...chatStyle.message.body}
      >
        <Box p={3} height="100%" width="100%" {...chatStyle.message.content}>
          {content}
        </Box>
        <ChatMessageFooter groupedMessages={groupedMessages} />
      </Flex>
    </Flex>
  );
};

export default ChatMessage;
