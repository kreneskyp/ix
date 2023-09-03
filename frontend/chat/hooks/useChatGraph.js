import { useDetailAPI } from "utils/hooks/useDetailAPI";

export const useChatGraph = (id) => {
  return useDetailAPI(`/api/chats/${id}/graph`);
};
