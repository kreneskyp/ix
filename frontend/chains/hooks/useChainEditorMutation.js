import { useMutation } from "react-relay/hooks";
import { useCallback } from "react";

export const useChainEditorMutation = ({
  chain,
  query,
  onCompleted: globalOnCompleted,
  onError: globalOnError,
}) => {
  const [commit, isInFlight] = useMutation(query);

  const callback = useCallback(
    (data = {}, { onError, onCompleted } = {}) => {
      commit({
        variables: { data },
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
    [commit, chain?.id]
  );

  return {
    callback,
    isInFlight,
  };
};
