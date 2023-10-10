import { Button, Icon, IconButton } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import React from "react";
import useCreateChat from "chat/hooks/useCreateChat";
import { useColorMode } from "@chakra-ui/color-mode";
import PlusMessageIcon from "components/PlusMessageIcon";

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
    <IconButton
      border="1px solid"
      borderColor={colorMode === "light" ? "gray.300" : "whiteAlpha.50"}
      icon={<PlusMessageIcon />}
      title={"New Chat"}
      onClick={handleCreate}
    />
  );
};
