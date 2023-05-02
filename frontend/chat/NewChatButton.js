import { Button, Icon } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import React from "react";
import useCreateChat from "chat/graphql/useCreateChat";
import { useColorMode } from "@chakra-ui/color-mode";

export const NewChatButton = () => {
  const { createChat } = useCreateChat();
  const { colorMode } = useColorMode();
  const handleCreate = async () => {
    try {
      await createChat();
    } catch (error) {
      toast({
        title: "Error starting task",
        description:
          error.message || "An error occurred while starting the task.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Button
      bg="transparent"
      width="100%"
      borderStyle="dashed"
      borderWidth="2px"
      borderColor={colorMode === "light" ? "gray.800" : "whiteAlpha.600"}
      color={colorMode === "light" ? "gray.900" : "whiteAlpha.800"}
      leftIcon={<Icon as={FontAwesomeIcon} icon={faPlus} />}
      onClick={handleCreate}
    >
      New Chat
    </Button>
  );
};
