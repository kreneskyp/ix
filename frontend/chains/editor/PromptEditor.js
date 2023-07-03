import React, { useCallback, useState } from "react";
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
import { SCROLLBAR_CSS } from "site/css";
import { NodeResizeControl } from "reactflow";

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
      <NodeResizeControl
        variant={"line"}
        minWidth={400}
        position={"left"}
        h={"100%"}
        style={{ border: "5px solid transparent" }}
      />

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
            css={SCROLLBAR_CSS}
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
      <NodeResizeControl
        variant={"line"}
        minWidth={400}
        h={"100%"}
        style={{ border: "5px solid transparent" }}
      />
    </VStack>
  );
};

export default PromptEditor;
