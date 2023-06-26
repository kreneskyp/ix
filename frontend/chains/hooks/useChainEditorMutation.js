import { useMutation } from "react-relay/hooks";
import { useCallback } from "react";

export const useChainEditorMutation = ({
  chain,
  query,
  onCompleted: globalOnCompleted,
  onError: globalOnError,
  reactFlowInstance,
}) => {
  const [commit, isInFlight] = useMutation(query);

  const callback = useCallback(
    (variables = {}, { onError, onCompleted } = {}) => {
      commit({
        variables,
        onCompleted: (response, errors) => {
          if (onCompleted) {
            onCompleted(response, errors);
          }
          if (globalOnCompleted) {
            globalOnCompleted(response, errors);
          }
        },
        onError: (err) => {
          if (onError) {
            onError(err);
          }
          if (globalOnError) {
            globalOnError(err);
          }
        },
      });
    },
    [commit, chain?.id, globalOnCompleted, globalOnError, reactFlowInstance]
  );

  return {
    callback,
    isInFlight,
  };
};
