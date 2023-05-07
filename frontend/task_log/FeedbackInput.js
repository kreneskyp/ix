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
import { useSendFeedback } from "chat/graphql/useSendFeedback";

const FeedbackInput = () => {
  const [feedback, setFeedback] = useState("");
  const { sendFeedback, error, loading } = useSendFeedback();
  const toast = useToast();

  const handleSendFeedback = async () => {
    const result = await sendFeedback(feedback);
    if (result) {
      setFeedback("");
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter") {
      handleSendFeedback();
    }
  };

  if (error) {
    toast({
      title: "Error sending feedback",
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
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          onKeyPress={handleKeyPress}
          isDisabled={loading}
          sx={{
            boxShadow: "0 0 5px rgba(0, 0, 0, 0.2)",
          }}
        />
        <InputRightElement>
          <Button
            onClick={handleSendFeedback}
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

export default FeedbackInput;
