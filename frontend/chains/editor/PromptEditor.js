import React, { useCallback, useState } from "react";
import { Button, Flex, Select, VStack, HStack, Text } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faTrashAlt,
  faPlus,
  faArrowUp,
  faArrowDown,
} from "@fortawesome/free-solid-svg-icons";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { PromptMessageInput } from "chains/editor/PromptMessageInput";

const ROLE_OPTIONS = ["user", "assistant"];

const DEFAULT_MESSAGE = {
  role: "user",
  template: "",
  input_variables: [],
  partial_variables: {},
};

const DEFAULT_MESSAGES = [
  {
    role: "system",
    template: "",
    input_variables: [],
    partial_variables: {},
  },
];

function parseVariables(str) {
  const regex = /(?<!{){([a-zA-Z0-9_]+)}(?!})/g;
  const matches = str.match(regex);

  if (!matches) {
    return [];
  }

  const variables = matches.map((match) => match.slice(1, -1));
  return variables;
}

const PromptEditor = ({ data, onChange }) => {
  const [messages, setMessages] = useState(data.messages || DEFAULT_MESSAGES);
  const { input, scrollbar } = useEditorColorMode();

  const handleOnChange = useCallback(
    (updatedMessages) => {
      if (onChange !== undefined) {
        onChange({ ...data, messages: updatedMessages });
      }
      setMessages(updatedMessages);
    },
    [onChange]
  );

  const addMessage = useCallback(() => {
    handleOnChange([...messages, { ...DEFAULT_MESSAGE }]);
  }, [handleOnChange, messages]);

  const deleteMessage = useCallback(
    (index) => {
      handleOnChange(messages.filter((_, idx) => idx !== index));
    },
    [handleOnChange, messages]
  );

  const moveMessage = useCallback(
    (index, direction) => {
      const updatedMessages = [...messages];
      const temp = updatedMessages[index];
      updatedMessages[index] = updatedMessages[index + direction];
      updatedMessages[index + direction] = temp;
      handleOnChange(updatedMessages);
    },
    [handleOnChange, messages]
  );

  const handleMessageChange = useCallback(
    (index, field, value) => {
      const updatedMessages = [...messages];
      const updatedMessage = { ...updatedMessages[index], [field]: value };

      // always updated variables after an edit.
      updatedMessage["input_variables"] = parseVariables(
        updatedMessage["template"]
      );

      updatedMessages[index] = updatedMessage;
      handleOnChange(updatedMessages);
    },
    [handleOnChange, messages]
  );

  return (
    <VStack spacing={1} align="stretch">
      {messages.map((message, index) => (
        <VStack key={index} py={2} spacing={2}>
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
                {...input}
                size={"sm"}
                borderRadius={5}
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

          <PromptMessageInput
            borderRadius={5}
            border="1px solid"
            p={2}
            width="100%"
            initialValue={message.template}
            placeholder="Enter template"
            onChange={(text) => handleMessageChange(index, "template", text)}
            {...input}
          />
        </VStack>
      ))}
      <Flex width="100%" justifyContent="flex-end">
        <Button
          width={140}
          leftIcon={<FontAwesomeIcon icon={faPlus} />}
          colorScheme="orange"
          onClick={addMessage}
          mr={2}
          size={"sm"}
        >
          Add Message
        </Button>
      </Flex>
    </VStack>
  );
};

export default PromptEditor;
