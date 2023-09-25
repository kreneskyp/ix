import React from "react";
import { ChatPane } from "chains/editor/ChatPane";
import { ChainState } from "chains/editor/contexts";
import { useTestChat } from "chains/hooks/useTestChat";
import { Center, Spinner, Text } from "@chakra-ui/react";

export const TestChatPane = () => {
  const { chain } = React.useContext(ChainState);
  const { chat } = useTestChat(chain?.id);

  if (!chain) {
    return (
      <Center height={"100%"}>
        <Text color={"gray.500"} fontSize={"sm"}>
          Please save the chain before testing the chat.
        </Text>
      </Center>
    );
  }

  if (!chat)
    return (
      <Center height={"100%"}>
        <Spinner size={"xl"} />
      </Center>
    );

  return <ChatPane chatId={chat.id} />;
};
