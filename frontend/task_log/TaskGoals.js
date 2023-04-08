import React from "react";
import { useTask } from "tasks/contexts";

export const TaskGoals = () => {
  const { task } = useTask();

  return <div>goals: {task.goals}</div>;
};

export default TaskGoals;
