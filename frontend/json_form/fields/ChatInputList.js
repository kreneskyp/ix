import React from "react";
import {
  Box,
  Input,
  InputGroup,
  InputRightElement,
  Tooltip,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faKeyboard } from "@fortawesome/free-solid-svg-icons";

import { HashList } from "json_form/fields/HashList";
import { useEditorColorMode } from "chains/editor/useColorMode";

const DEFAULT_INPUT = { name: "", is_chat: false };

const ChatInput = ({ value, onChange }) => {
  const style = useEditorColorMode();

  // Backwards compatibility for string values
  const _value = React.useMemo(
    () => (typeof value === "object" ? value : { value, is_chat: false }),
    [value]
  );

  const isChat = _value?.is_chat === true;

  const handleIconClick = () => {
    onChange({
      target: { value: { ...(_value || DEFAULT_INPUT), is_chat: !isChat } },
    });
  };

  const handleInputChange = (e) => {
    onChange({
      target: {
        value: { ...(_value || DEFAULT_INPUT), value: e.target.value },
      },
    });
  };

  const iconStyle = {
    cursor: "pointer",
    color: isChat ? "blue.400" : style.isLight ? "gray.400" : "gray.600",
  };

  return (
    <InputGroup>
      <Input
        value={_value.value}
        onChange={handleInputChange}
        placeholder={"enter value"}
        {...style.input}
      />
      <InputRightElement>
        <Tooltip label={`${isChat ? "Is chat" : "Make chat"}`}>
          <Box onClick={handleIconClick} {...iconStyle}>
            <FontAwesomeIcon icon={faKeyboard} />
          </Box>
        </Tooltip>
      </InputRightElement>
    </InputGroup>
  );
};

export const ChatInputList = ({ config, name, onChange }) => {
  const handleChange = (newConfig) => {
    // ensure only a single input selected as chat_input
    // find index of existing chat
    const chat_index = config[name]?.findIndex((item) => item.is_chat === true);

    if (chat_index > -1) {
      // find first index with is_chat that isn't the chat_index
      const next_chat_index = newConfig[name]?.findIndex(
        (item, index) => item.is_chat === true && index !== chat_index
      );

      // clear is_chat for any that is NOT the next_chat_index
      if (next_chat_index > -1) {
        for (let i = 0; i < newConfig[name].length; i++) {
          if (i !== next_chat_index) {
            newConfig[name][i].is_chat = false;
          }
        }
      }
    }
    onChange(newConfig);
  };

  return (
    <HashList
      name={name}
      component={ChatInput}
      defaultValue={DEFAULT_INPUT}
      onChange={handleChange}
      config={config}
      isRequired={true}
    />
  );
};
