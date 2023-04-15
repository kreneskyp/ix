import React, { createContext, useContext, useState, useCallback } from "react";
import { UserContext } from "users/contexts";
import { graphql, useLazyLoadQuery, useRefetch } from "react-relay/hooks";

export const TasksContext = createContext(null);
export const TaskContext = createContext(null);

const tasksQuery = graphql`
  query contexts_tasks_Query {
    tasks {
      id
      isComplete
      createdAt
      completeAt
    }
  }
`;

export const TasksProvider = ({ children }) => {
  const { tasks } = useLazyLoadQuery(tasksQuery, {});

  return (
    <TasksContext.Provider value={tasks}>{children}</TasksContext.Provider>
  );
};

export function TaskProvider({ children, taskId }) {
  const user = useContext(UserContext);
  const [refreshedQueryOptions, setRefreshedQueryOptions] = useState(null);

  const refresh = useCallback(() => {
    setRefreshedQueryOptions((prev) => ({
      fetchKey: (prev?.fetchKey ?? 0) + 1,
      fetchPolicy: "network-only",
    }));
  }, []);

  const data = useLazyLoadQuery(
    graphql`
      query contexts_task_Query($id: ID!) {
        task(id: $id) {
          id
          isComplete
          completeAt
          goals {
            description
            complete
          }
        }
      }
    `,
    { id: taskId },
    refreshedQueryOptions ?? { fetchPolicy: "store-or-network" }
  );

  return (
    <TaskContext.Provider value={{ task: data.task, user, refresh }}>
      {children}
    </TaskContext.Provider>
  );
}

export const useTask = () => {
  return useContext(TaskContext);
};

export const useTasks = () => {
  return useContext(TasksContext);
};

export function useUser() {
  const context = useTask();
  if (context === null) {
    throw new Error("useUser must be used within a TaskProvider");
  }
  return context.user;
}
