import React from "react";
import { Button, useToast } from "@chakra-ui/react";
import {useAuthorizeCommand} from "chat/graphql/useAuthorizeCommand";

export const AuthorizeCommandButton = ({ messageId }) => {
  const { authorizeCommand, error, loading } = useAuthorizeCommand();
  const toast = useToast();

  const handleClick = async () => {
    const success = await authorizeCommand(messageId);
    if (success) {
      // Handle success, e.g. display a success toast or update the UI
    } else {
      // Display an error toast
      toast({
        title: "Error",
        description: "Failed to authorize the command.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Button
      colorScheme="blue"
      isLoading={loading}
      onClick={handleClick}
      disabled={!messageId}
    >
      Authorize Command
    </Button>
  );
};

export default AuthorizeCommandButton;
