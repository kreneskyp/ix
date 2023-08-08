import { useCallback, useState } from "react";
import axios from "axios";

const useUpdateAPI = (url, { onSuccess, onError } = {}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const update = useCallback(
    async (data) => {
      setIsLoading(true);
      try {
        const response = await axios.put(url, data);
        setIsLoading(false);
        return response.data;
      } catch (err) {
        setIsLoading(false);
        setError(err);
        throw err;
      }
    },
    [url]
  );

  return {
    update,
    isLoading,
    error,
  };
};

export default useUpdateAPI;
