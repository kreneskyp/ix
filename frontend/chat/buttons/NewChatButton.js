import React from "react";
import useCreateChat from "chat/hooks/useCreateChat";
import PlusMessageIcon from "components/PlusMessageIcon";
import { MenuItem } from "site/MenuItem";

export const NewChatButton = () => {
  const { createChat } = useCreateChat();
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
    <MenuItem title={"New Chat"} onClick={handleCreate}>
      <PlusMessageIcon />
    </MenuItem>
  );
};
