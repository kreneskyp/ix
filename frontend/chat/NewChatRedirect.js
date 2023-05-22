import React from "react";

import useCreateChat from "chat/graphql/useCreateChat";
import { Spinner } from "@chakra-ui/react";
import { useEffect } from "react";

export const NewChatRedirect = () => {
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

  useEffect(() => {
    handleCreate();
  }, []);

  return <Spinner />;
};
