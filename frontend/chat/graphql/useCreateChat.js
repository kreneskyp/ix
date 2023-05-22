import { useMutation, graphql } from "react-relay/hooks";
import { useNavigate } from "react-router-dom";

const CREATE_CHAT_MUTATION = graphql`
  mutation useCreateChatMutation {
    createChat {
      chat {
        id
      }
    }
  }
`;

function useCreateChat() {
  const [commit, isInFlight] = useMutation(CREATE_CHAT_MUTATION);
  const navigate = useNavigate();

  const createChat = () => {
    commit({
      onCompleted: (data, errors) => {
        if (errors) {
          console.error(errors);
        }
        navigate(`/chat/${data.createChat.chat.id}`);
      },
      onError: (error) => {
        console.error(error);
      },
    });
  };

  return { createChat, isInFlight };
}

export default useCreateChat;
