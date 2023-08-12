import { useCallback, useState } from "react";
import axios from "axios";

export const useAxios = (
  { onSuccess, onError, method = "get" } = {},
  dependencies = []
) => {
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const onSuccessGlobal = onSuccess;
  const onErrorGlobal = onError;

  const call = useCallback(async (url, { data, onSuccess, onError } = {}) => {
    setIsLoading(true);

    try {
      const args = data ? [url, data] : [url];
      const _response = await axios[method](...args);
      if (onSuccessGlobal) {
        onSuccessGlobal(_response);
      }
      if (onSuccess) {
        onSuccess(_response);
      }
      setResponse(_response);
      return _response;
    } catch (err) {
      setError(err);
      if (onErrorGlobal) {
        onErrorGlobal(err);
      }
      if (onError) {
        onError(err);
      }
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, dependencies);

  return {
    call,
    response,
    isLoading,
    error,
  };
};
