import { useState } from "react";
import { useMutation, graphql } from "react-relay/hooks";

const AUTHORIZE_COMMAND_MUTATION = graphql`
  mutation useAuthorizeCommandMutation($input: CommandAuthorizeInput!) {
    authorizeCommand(input: $input) {
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

export const useAuthorizeCommand = () => {
  const [commit, isInFlight] = useMutation(AUTHORIZE_COMMAND_MUTATION);
  const [error, setError] = useState(null);

  const authorizeCommand = (messageId) => {
    return new Promise((resolve) => {
      commit({
        variables: {
          input: {
            messageId: messageId,
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

  return { authorizeCommand, error, loading: isInFlight };
};
