import React, { useState } from "react";
import {
  Input,
  InputGroup,
  InputRightElement,
  Button,
  Flex,
  Spacer,
  IconButton,
  useToast,
  Icon,
} from "@chakra-ui/react";
import { ArrowForwardIcon, CheckIcon, CloseIcon } from "@chakra-ui/icons";
import { useMutation, graphql } from "react-relay/hooks";
import { useLatestTaskLog } from "task_log/contexts";

const feedbackMutation = graphql`
  mutation TaskResponseFormMutation($input: TaskLogResponseInput!) {
    respondToTaskMsg(input: $input) {
      taskLogMessage {
        id
        role
        content {
          ... on FeedbackContentType {
            feedback
          }
        }
      }
      errors
    }
  }
`;

export const TaskResponseForm = ({ onRespond }) => {
  const message = useLatestTaskLog();
  const [response, setResponse] = useState("");
  const toast = useToast();

  const [mutate, isLoading] = useMutation(feedbackMutation);

  function handleSubmit(event) {
    event.preventDefault();
    if (response) {
      mutate({
        variables: {
          input: {
            id: message.id,
            response,
          },
        },
        onCompleted: (response, errors) => {
          if (errors) {
            toast({
              title: "Error",
              description: errors[0].message,
              status: "error",
              duration: 5000,
              isClosable: true,
            });
          }
        },
      });
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <InputGroup>
        <Input
          type="text"
          width={800}
          placeholder="Enter additional feedback."
          value={response}
          onChange={(event) => setResponse(event.target.value)}
          onKeyPress={(event) => {
            if (event.key === "Enter") {
              handleSubmit(event);
            }
          }}
          sx={{
            boxShadow: "0 0 5px rgba(0, 0, 0, 0.2)",
          }}
        />
        <InputRightElement>
          <Button
            type="submit"
            isLoading={isLoading}
            size="sm"
            bg="none"
            _hover={{ bg: "none" }}
          >
            <Icon as={ArrowForwardIcon} />
          </Button>
        </InputRightElement>
      </InputGroup>
    </form>
  );
};

export default TaskResponseForm;
