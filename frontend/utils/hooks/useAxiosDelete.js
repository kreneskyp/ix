import { useAxios } from "utils/hooks/useAxios";

export const useAxiosDelete = (
  { onSuccess, onError } = {},
  dependencies = []
) => {
  return useAxios({ onSuccess, onError, method: "delete" }, dependencies);
};
