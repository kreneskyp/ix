import React, { createContext, useContext } from "react";
import { graphql } from "react-relay";
import { AgentContext } from "agents/contexts";
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
          assistantTimestamp
          userTimestamp
          command
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
  const task = useContext(TaskContext);
  const taskLogs = useContext(TaskLogContext);

  if (!task || !taskLogs) {
    return null;
  }

  const latestTaskLog = taskLogs
    .filter((log) => log.taskId === task.id)
    .sort((a, b) => b.startedAt.localeCompare(a.startedAt))
    .shift();

  return latestTaskLog;
};
