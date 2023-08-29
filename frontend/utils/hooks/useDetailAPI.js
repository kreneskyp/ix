import { useAxios } from "utils/hooks/useAxios";
import { useCallback } from "react";

export const useDetailAPI = (
  url,
  { onSuccess, onError, auto = false } = {},
  dependencies = []
) => {
  const { call, isLoading, error, response } = useAxios(
    { onSuccess, onError, method: "get" },
    dependencies
  );

  const get = useCallback(
    (args) => {
      return call(url, ...(args || []));
    },
    [url, call]
  );

  return {
    response,
    call: get,
    isLoading,
    error,
  };
};
