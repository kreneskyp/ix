import { useCallback, useState } from "react";
import axios from "axios";

export const useDeleteAPI = (endpoint) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const deleteData = useCallback(async () => {
    setIsLoading(true);
    try {
      await axios.delete(endpoint);
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, [endpoint]);

  return {
    call: deleteData,
    isLoading,
    error,
  };
};
