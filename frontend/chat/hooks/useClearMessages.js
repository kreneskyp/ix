import { useAxios } from "utils/hooks/useAxios";
import React from "react";

export const useClearMessages = (chatId) => {
  // callback: reset messages
  const { call, isLoading } = useAxios({
    method: "post",
  });
  const clearMessages = React.useCallback(() => {
    call(`/api/chats/${chatId}/messages/clear`);
  }, [call, chatId]);

  return {
    clearMessages,
    isLoading,
  };
};
