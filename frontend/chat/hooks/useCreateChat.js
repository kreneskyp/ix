import { useNavigate } from "react-router-dom";
import useUpdateAPI from "utils/hooks/useUpdateAPI";

function useCreateChat() {
  const { call, isLoading } = useUpdateAPI(`/api/chats/`, { method: "post" });
  const navigate = useNavigate();

  const createChat = () => {
    call(
      { name: "" },
      {
        onSuccess: (response) => {
          navigate(`/chat/${response.data.id}`);
        },
        onError: (error) => {
          console.error(error);
        },
      }
    );
  };

  return { createChat, isLoading };
}

export default useCreateChat;
