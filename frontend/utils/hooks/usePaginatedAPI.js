import { useCallback, useEffect, useState } from "react";
import axios from "axios";

export function usePaginatedAPI(
  endpoint,
  { offset = 0, limit = 10, load = true, loadDependencies = [] } = {}
) {
  const [page, setPage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const _load = useCallback(
    async (args = {}) => {
      setIsLoading(true);
      const params = { limit, offset, ...args };
      try {
        const response = await axios.get(endpoint, {
          params,
        });
        setPage(response.data);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      } finally {
        setIsLoading(false);
      }
    },
    [endpoint]
  );

  useEffect(() => {
    if (load) {
      _load();
    }
  }, [_load, ...loadDependencies]);

  return {
    page,
    isLoading,
    load: _load,
  };
}
