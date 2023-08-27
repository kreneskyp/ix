import { Button, Icon } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import React from "react";
import useCreateChat from "chat/hooks/useCreateChat";
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
      border="1px solid"
      borderColor={colorMode === "light" ? "gray.300" : "whiteAlpha.50"}
      width="100%"
      leftIcon={<Icon as={FontAwesomeIcon} icon={faPlus} />}
      onClick={handleCreate}
    >
      New Chat
    </Button>
  );
};
