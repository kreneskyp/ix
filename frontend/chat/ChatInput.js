import React, { useState } from "react";
import {
  Box,
  Input,
  InputGroup,
  InputRightElement,
  Button,
  useToast,
  Icon,
} from "@chakra-ui/react";
import { ArrowForwardIcon } from "@chakra-ui/icons";
import { useSendInput } from "chat/graphql/useSendInput";

const ChatInput = ({ chat }) => {
  const [input, setInput] = useState("");
  const { sendFeedback: sendInput, error, loading } = useSendInput(chat.id);
  const toast = useToast();

  const handleSendInput = async () => {
    const result = await sendInput(input);
    if (result) {
      setInput("");
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter") {
      handleSendInput();
    }
  };

  if (error) {
    toast({
      title: "Error sending input",
      description: error.message,
      status: "error",
      duration: 3000,
      isClosable: true,
    });
  }

  return (
    <Box display="flex" alignItems="center">
      <InputGroup>
        <Input
          type="text"
          width={800}
          placeholder="What can I help you with?"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          isDisabled={loading}
          sx={{
            boxShadow: "0 0 5px rgba(0, 0, 0, 0.2)",
          }}
        />
        <InputRightElement>
          <Button
            onClick={handleSendInput}
            isLoading={loading}
            size="sm"
            bg="none"
            _hover={{ bg: "none" }}
          >
            <Icon as={ArrowForwardIcon} />
          </Button>
        </InputRightElement>
      </InputGroup>
    </Box>
  );
};

export default ChatInput;
