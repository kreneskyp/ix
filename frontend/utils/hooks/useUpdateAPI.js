import { useCallback } from "react";
import { useAxios } from "utils/hooks/useAxios";

const useUpdateAPI = (
  url,
  { onSuccess, onError, method = "put", dependencies = [] } = {}
) => {
  const { call, isLoading, error, response } = useAxios(
    { onSuccess, onError, method },
    dependencies
  );

  const update = useCallback(
    (data, config = {}) => {
      return call(url, { data, ...config });
    },
    [url, call]
  );

  return {
    call: update,
    response,
    isLoading,
    error,
  };
};

export default useUpdateAPI;
