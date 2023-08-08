import { useState, useEffect, useCallback } from "react";
import axios from "axios";

export const useDetailAPI = (endpoint, { load = true } = {}) => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(endpoint);
      setData(response.data);
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, [endpoint]);

  useEffect(() => {
    if (load) {
      loadData();
    }
  }, [endpoint, load]);

  return {
    data,
    load: loadData,
    isLoading,
    error,
  };
};
