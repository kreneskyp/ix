import React, { useState, useEffect } from "react";
import ChatMessage from "chat/ChatMessage";
import { fetchQuery, graphql } from "relay-runtime";
import { useTask } from "tasks/contexts";
import environment from "relay-environment";
import { TaskLogMessagesQuery } from "task_log/graphql/TaskLogMessagesQuery";

const TaskLogMessageStream = () => {
  const [taskLogMessages, setMessages] = useState([]);
  const { task } = useTask();

  useEffect(() => {
    const fetchTaskLogMessages = async () => {
      const variables = {
        taskId: task.id,
      };
      const observable = fetchQuery(
        environment,
        TaskLogMessagesQuery,
        variables
      );

      const subscription = observable.subscribe({
        next: (response) => {
          if (response.taskLogMessages) {
            setMessages(response.taskLogMessages);
          }
        },
        error: (error) => console.error(error),
      });

      return () => subscription.unsubscribe();
    };

    // initial fetch
    fetchTaskLogMessages();

    const interval = setInterval(() => {
      fetchTaskLogMessages();
    }, 4000);
    return () => clearInterval(interval);
  }, [task]);

  return (
    <>
      {taskLogMessages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}
    </>
  );
};

export default TaskLogMessageStream;
