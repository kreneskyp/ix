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
import {useLatestTaskLog} from "task_log/contexts";

const responseMutation = graphql`
  mutation TaskResponseFormMutation($input: TaskLogResponseInput!) {
    respondToTaskMsg(input: $input) {
      taskLogMessage {
        userResponse
        authorized
      }
    }
  }
`;

export const TaskResponseForm = ({ onRespond }) => {
  const message = useLatestTaskLog()
  const [response, setResponse] = useState("");
  const [isAuthorized, setIsAuthorized] = useState(true); // defaults to "Yes" button

  const toast = useToast();

  const [mutate, isLoading] = useMutation(responseMutation);

  function handleSubmit(event) {
    event.preventDefault();
    if (response) {
      mutate({
        variables: {
          input: {
            id: message.id,
            response,
            isAuthorized,
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
          } else {
            onRespond(response.respondToTaskLog.taskLog);
            toast({
              title: "Success",
              description: "Your response has been recorded.",
              status: "success",
              duration: 3000,
              isClosable: true,
            });
          }
        },
      });
    } else {
      setIsAuthorized(true); // default to "Yes" if no response message
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <InputGroup>
        <Button
          colorScheme={isAuthorized ? "green" : "red"}
          variant="outline"
          onClick={() => setIsAuthorized(true)}
          marginRight="5px"
        >
          <CheckIcon marginRight="2px" />
          Yes
        </Button>
        <Button
          colorScheme={!isAuthorized ? "green" : "red"}
          variant="outline"
          onClick={() => setIsAuthorized(false)}
          marginRight="5px"
        >
          <CloseIcon marginRight="2px" />
          No
        </Button>
        <Input
          type="text"
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
