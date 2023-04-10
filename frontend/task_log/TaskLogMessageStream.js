import React from "react";
import { useTaskLogMessages } from "task_log/contexts";
import { TaskLogMessage } from "task_log/TaskLogMessage";
import { VStack, Flex } from "@chakra-ui/react";
import ChatMessage from "chat/ChatMessage";

export const TaskLogMessageStream = () => {
  const { taskLogMessages } = useTaskLogMessages();

  let messages;
  if (taskLogMessages !== undefined && taskLogMessages !== null) {
    messages = taskLogMessages.map((message) => (
      <ChatMessage key={message.id} message={message} />
    ));
  }

  return <VStack>{messages}</VStack>;
};

export default TaskLogMessageStream;
