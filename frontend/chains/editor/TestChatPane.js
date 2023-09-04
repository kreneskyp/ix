import React from "react";
import { ChatPane } from "chains/editor/ChatPane";
import { ChainState } from "chains/editor/contexts";
import { useTestChat } from "chains/hooks/useTestChat";
import { Center, Spinner } from "@chakra-ui/react";

export const TestChatPane = () => {
  const { chain } = React.useContext(ChainState);
  const { chat } = useTestChat(chain?.id);

  if (!chat)
    return (
      <Center height={"100%"}>
        <Spinner size={"xl"} />
      </Center>
    );

  return <ChatPane chatId={chat.id} />;
};
