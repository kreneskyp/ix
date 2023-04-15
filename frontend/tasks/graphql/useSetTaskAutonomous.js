import { useMutation, graphql } from "react-relay/hooks";

const SET_TASK_AUTONOMOUS_MUTATION = graphql`
  mutation useSetTaskAutonomousMutation($taskId: ID!, $autonomous: Boolean!) {
    setTaskAutonomous(taskId: $taskId, autonomous: $autonomous) {
      task {
        id
        autonomous
      }
    }
  }
`;

function useSetTaskAutonomous() {
  const [commit, isInFlight] = useMutation(SET_TASK_AUTONOMOUS_MUTATION);

  const setTaskAutonomous = (taskId, autonomous) => {
    commit({
      variables: { taskId, autonomous },
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

  return { setTaskAutonomous, isInFlight };
}

export default useSetTaskAutonomous;
