import React, { createContext, useContext, useState, useCallback } from "react";
import { UserContext } from "users/contexts";
import { graphql, useLazyLoadQuery } from "react-relay/hooks";

export const TaskContext = createContext(null);

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
      query contexts_task_Query($id: UUID!) {
        task(id: $id) {
          id
          isComplete
          completeAt
          autonomous
          agent {
            id
            name
            model
            purpose
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

export function useUser() {
  const context = useTask();
  if (context === null) {
    throw new Error("useUser must be used within a TaskProvider");
  }
  return context.user;
}
