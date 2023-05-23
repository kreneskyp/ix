import React, { useState } from "react";
import {
  Button,
  Flex,
  Textarea,
  Select,
  VStack,
  HStack,
  Text,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faTrashAlt,
  faPlus,
  faArrowUp,
  faArrowDown,
} from "@fortawesome/free-solid-svg-icons";

const ROLE_OPTIONS = ["user", "assistant"];

const DEFAULT_MESSAGE = {
  role: "user",
  template: "",
  input_variables: [],
  partial_variables: {},
};

const PromptEditor = () => {
  const [messages, setMessages] = useState([
    {
      role: "system",
      template: "CREATE_PLAN_V3",
      input_variables: ["foo", "bar"],
      partial_variables: {
        format: "PLAN_FORMAT_V3",
        artifact_format: "ARTIFACT_FORMAT",
      },
    },
  ]);

  const addMessage = () => {
    setMessages([...messages, { ...DEFAULT_MESSAGE }]);
  };

  const deleteMessage = (index) => {
    setMessages(messages.filter((_, idx) => idx !== index));
  };

  const moveMessage = (index, direction) => {
    const messagesCopy = [...messages];
    const temp = messagesCopy[index];
    messagesCopy[index] = messagesCopy[index + direction];
    messagesCopy[index + direction] = temp;
    setMessages(messagesCopy);
  };

  const handleMessageChange = (index, field, value) => {
    const messagesCopy = [...messages];
    messagesCopy[index][field] = value;
    setMessages(messagesCopy);
  };

  return (
    <VStack spacing={1} align="stretch">
      {messages.map((message, index) => (
        <VStack key={index} p={2} spacing={2}>
          <Flex
            alignItems="center"
            justifyContent="space-between"
            width="100%"
            height="100%"
          >
            {index === 0 ? (
              <Text fontWeight="bold">System</Text>
            ) : (
              <Select
                width={125}
                value={message.role}
                onChange={(e) =>
                  handleMessageChange(index, "role", e.target.value)
                }
              >
                {ROLE_OPTIONS.map((role) => (
                  <option key={role} value={role}>
                    {role}
                  </option>
                ))}
              </Select>
            )}
            <HStack spacing={5}>
              {index > 1 && (
                <FontAwesomeIcon
                  icon={faArrowUp}
                  cursor="pointer"
                  onClick={() => moveMessage(index, -1)}
                />
              )}
              {index && index < messages.length - 1 && (
                <FontAwesomeIcon
                  icon={faArrowDown}
                  cursor="pointer"
                  onClick={() => moveMessage(index, 1)}
                />
              )}
              {index > 0 && (
                <FontAwesomeIcon
                  icon={faTrashAlt}
                  cursor="pointer"
                  onClick={() => deleteMessage(index)}
                />
              )}
            </HStack>
          </Flex>
          <Textarea
            width="100%"
            value={message.template}
            placeholder="Enter template"
            onChange={(e) =>
              handleMessageChange(index, "template", e.target.value)
            }
            isRequired
          />
        </VStack>
      ))}
      <Flex width="100%" justifyContent="flex-end">
        <Button
          width={140}
          leftIcon={<FontAwesomeIcon icon={faPlus} />}
          colorScheme="orange"
          onClick={addMessage}
          mr={4}
        >
          Add Message
        </Button>
      </Flex>
    </VStack>
  );
};

export default PromptEditor;
