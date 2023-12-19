import { useCallback, useState } from "react";
import axios from "axios";

export const useSendInput = (chat_id) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const url = `/api/chats/${chat_id}/messages`;

  const sendInput = useCallback(
    async (text, artifact_ids) => {
      const data = {
        chat_id: chat_id,
        text: text,
        artifact_ids: artifact_ids || [],
      };

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
    [chat_id]
  );

  return {
    sendInput,
    isLoading,
    error,
  };
};
