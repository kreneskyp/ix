import { useDetailAPI } from "utils/hooks/useDetailAPI";

export const useChain = (id) => {
  return useDetailAPI(`/api/chains/${id}`, { auto: true });
};
