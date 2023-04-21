import { useMutation, graphql } from "react-relay/hooks";

const START_TASK_MUTATION = graphql`
  mutation useStartTaskMutation($taskId: UUID!) {
    startTask(taskId: $taskId) {
      task {
        id
      }
    }
  }
`;

function useStartTask() {
  const [commit, isInFlight] = useMutation(START_TASK_MUTATION);

  const startTask = (taskId) => {
    commit({
      variables: { taskId },
      onCompleted: (data, errors) => {
        if (errors) {
          console.error(errors);
        }
      },
      onError: (error) => {
        console.error(error);
      },
    });
  };

  return { startTask, isInFlight };
}

export default useStartTask;
