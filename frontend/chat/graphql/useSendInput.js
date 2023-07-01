import { useCallback, useState } from "react";
import { useMutation, graphql } from "react-relay/hooks";

const SEND_FEEDBACK_MUTATION = graphql`
  mutation useSendInputMutation($input: ChatInput!) {
    sendInput(input: $input) {
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

export const useSendInput = (chat_id) => {
  const [commit, isInFlight] = useMutation(SEND_FEEDBACK_MUTATION);
  const [error, setError] = useState(null);

  const sendInput = useCallback(
    (text) => {
      return commit({
        variables: {
          input: {
            chatId: chat_id,
            text,
          },
        },
        onCompleted: (response, errors) => {
          if (errors) {
            setError(errors[0]);
          } else {
            setError(null);
          }
        },
        onError: (err) => {
          setError(err);
        },
      });
    },
    [chat_id]
  );

  return { sendInput, error, loading: isInFlight };
};
