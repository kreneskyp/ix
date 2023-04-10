import React, { createContext, useContext } from "react";
import { graphql } from "react-relay";
import { TaskContext } from "tasks/contexts";
import { useLazyLoadQuery } from "react-relay/hooks";

export const TaskLogContext = createContext(null);

export function TaskLogProvider({ children }) {
  const { task } = useContext(TaskContext);
  const { taskLogMessages } = useLazyLoadQuery(
    graphql`
      query contexts_task_log_Query($taskId: ID!) {
        taskLogMessages(taskId: $taskId) {
          id
          role
          createdAt
          content {
            __typename
            ... on AssistantContentType {
              type
              thoughts {
                text
                reasoning
                plan
                criticism
                speak
              }
              command {
                name
                args
              }
            }
            ... on FeedbackRequestContentType {
              type
              message
            }
            ... on FeedbackContentType {
              type
              feedback
            }
            ... on SystemContentType {
              type
              message
            }
          }
          agent {
            id
            name
          }
        }
      }
    `,
    { taskId: task.id }
  );

  return (
    <TaskLogContext.Provider value={{ taskLogMessages }}>
      {children}
    </TaskLogContext.Provider>
  );
}

export function useTaskLogMessages() {
  const context = useContext(TaskLogContext);
  if (context === null) {
    throw new Error("useTaskLogs must be used within a TaskLogProvider");
  }
  return context;
}

export const useLatestTaskLog = () => {
  const taskLogMessages = useContext(TaskLogContext);

  if (!taskLogMessages || !taskLogMessages.taskLogMessages) {
    return null;
  }

  const latestTaskLogMessage = taskLogMessages.taskLogMessages
    .slice()
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt))
    .shift();

  return latestTaskLogMessage;
};
