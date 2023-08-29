import { useCallback, useState } from "react";
import axios from "axios";

const useCreateAPI = (url) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const create = useCallback(
    async (data) => {
      setIsLoading(true);
      try {
        const response = await axios.post(url, data);
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
    create,
    isLoading,
    error,
  };
};

export default useCreateAPI;
