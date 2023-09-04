import React from "react";
import { useAxios } from "utils/hooks/useAxios";
import { useDetailAPI } from "utils/hooks/useDetailAPI";

export const useTestChat = (chain_id) => {
  // api query: load chat
  const {
    call: loadChat,
    response,
    isLoading,
  } = useDetailAPI(`/api/chains/${chain_id}/chat`, { auto: false }, [chain_id]);

  const chat = response?.data;

  React.useEffect(() => {
    if (chain_id && !chat) {
      loadChat();
    }
  }, [chain_id]);

  // callback: reset messages
  const { call: ajaxPost, isLoading: isLoadingResetMsg } = useAxios({
    method: "post",
  });
  const { call: resetMessages } = React.useCallback(() => {
    ajaxPost(`/api/chats/${chat?.id}/reset`);
  }, [ajaxPost, chat?.id]);

  return {
    chat,
    isLoading: isLoading || isLoadingResetMsg,
    resetMessages,
  };
};
