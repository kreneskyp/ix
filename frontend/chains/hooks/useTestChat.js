import React from "react";
import { useDetailAPI } from "utils/hooks/useDetailAPI";

export const useTestChat = (chain_id) => {
  // api query: load chat
  const {
    call: loadChat,
    response,
    isLoading,
  } = useDetailAPI(`/api/chains/${chain_id}/chat`, { auto: false }, [chain_id]);

  const chat = chain_id === undefined ? null : response?.data;

  React.useEffect(() => {
    if (chain_id && !chat) {
      loadChat();
    }
  }, [chain_id]);

  return {
    chat,
    loadChat,
    isLoading,
  };
};
