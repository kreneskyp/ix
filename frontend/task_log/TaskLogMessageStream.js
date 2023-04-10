import React from "react";
import { useTaskLogMessages } from "task_log/contexts";
import { TaskLogMessage } from "task_log/TaskLogMessage";
import { VStack, Flex } from "@chakra-ui/react";
import ChatMessage from "chat/ChatMessage";

export const TaskLogMessageStream = () => {
  const { taskLogMessages } = useTaskLogMessages();

  // XXX: just using reverse for now because sorting in graphql is a pain
  let messages;
  if (taskLogMessages !== undefined && taskLogMessages !== null) {
    messages = taskLogMessages
      .toReversed()
      .map((message) => <ChatMessage key={message.id} message={message} />);
  }

  return (
    <>
      {/* Scrollable content */}
      {messages}
    </>
  );
};

export default TaskLogMessageStream;
