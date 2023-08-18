import React from "react";
import { Button, useToast } from "@chakra-ui/react";

export const AuthorizeCommandButton = ({ messageId }) => {
  // no-op until this endpoint is created.
  const authorizeCommand = () => {};
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
