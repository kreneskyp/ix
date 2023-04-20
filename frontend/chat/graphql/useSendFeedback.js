import { useState } from "react";
import { useMutation, graphql } from "react-relay/hooks";
import { useTask } from "tasks/contexts";

const SEND_FEEDBACK_MUTATION = graphql`
  mutation useSendFeedbackMutation($input: TaskFeedbackInput!) {
    sendFeedback(input: $input) {
      taskLogMessage {
        id
        role
        content
        parent {
          id
        }
      }
      errors
    }
  }
`;

export const useSendFeedback = () => {
  const { task } = useTask();
  const [commit, isInFlight] = useMutation(SEND_FEEDBACK_MUTATION);
  const [error, setError] = useState(null);

  const sendFeedback = (feedback) => {
    return new Promise((resolve) => {
      commit({
        variables: {
          input: {
            taskId: task.id,
            feedback,
          },
        },
        onCompleted: (response, errors) => {
          if (errors) {
            setError(errors[0]);
            resolve(false);
          } else {
            setError(null);
            resolve(true);
          }
        },
        onError: (err) => {
          setError(err);
          resolve(false);
        },
      });
    });
  };

  return { sendFeedback, error, loading: isInFlight };
};
