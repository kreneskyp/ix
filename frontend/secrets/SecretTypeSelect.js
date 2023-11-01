import React, { useState, useRef, useEffect } from "react";
import {
  Spinner,
  Select,
  HStack,
  Input,
  InputGroup,
  InputRightAddon,
  Flex,
  FormHelperText,
  Text,
  Tooltip,
  VStack,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlusCircle, faAngleLeft } from "@fortawesome/free-solid-svg-icons";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const SecretTypeSelect = ({
  data,
  onChange,
  onNew,
  api,
  disabled,
  ...props
}) => {
  const style = useEditorColorMode();
  const [showInput, setShowInput] = useState(false);
  const inputRef = useRef(null);
  const { page, isLoading } = usePaginatedAPI("/api/secret_types/", {
    limit: 1000,
  });

  const toggleInput = () => {
    setShowInput(!showInput);
    if (showInput) {
      onChange({
        type_key: null,
      });
    } else {
      onChange({
        type_id: null,
      });
    }
    if (onNew) {
      onNew(!showInput);
    }
  };

  const onTypeChange = (e) => {
    onChange({
      type_id: e.target.value,
    });
  };

  const onKeyChange = (e) => {
    onChange({
      type_key: e.target.value,
    });
  };

  useEffect(() => {
    if (showInput) {
      inputRef.current.focus();
    }
  }, [showInput]);

  if (isLoading) {
    return <Spinner />;
  }

  return (
    <VStack spacing={0} alignItems="start" width="100%" {...props}>
      <HStack spacing={0} width="100%">
        {showInput ? (
          <InputGroup>
            <Input
              ml={6}
              ref={inputRef}
              value={data?.type_key || ""}
              onChange={onKeyChange}
              placeholder="Enter type key"
              aria-label="Enter type key"
              paddingRight="40px"
              {...style.input}
            />
            <InputRightAddon
              {...style.input}
              px={0}
              pr={2}
              fontSize={"xs"}
              onClick={toggleInput}
              cursor={"pointer"}
            >
              <Tooltip label="choose existing type">
                <Text height="100%" pt={2} pl={4} mx={0} width={8}>
                  <FontAwesomeIcon icon={faAngleLeft} cursor="pointer" />
                </Text>
              </Tooltip>
            </InputRightAddon>
          </InputGroup>
        ) : (
          <>
            {!disabled && (
              <Tooltip label="create new type">
                <Text
                  as="span"
                  color={"green.300"}
                  mr={2}
                  cursor="pointer"
                  onClick={toggleInput}
                >
                  <FontAwesomeIcon icon={faPlusCircle} />
                </Text>
              </Tooltip>
            )}
            <Select
              value={data?.type_id || ""}
              onChange={onTypeChange}
              placeholder={"Select a type"}
              disabled={disabled || false}
              ml={disabled ? 6 : 0}
              {...style.input}
            >
              {page?.objects?.map((secret_type) => (
                <option key={secret_type.id} value={secret_type.id}>
                  {secret_type.name}
                </option>
              ))}
            </Select>
          </>
        )}
      </HStack>
      {!disabled && (
        <FormHelperText ml={7} fontSize="xs">
          {showInput
            ? "Key used to reference this type of secret, example: OPENAI_API_KEY, METAPHOR_API_KEY"
            : "Choose the type of secret or account to store."}
        </FormHelperText>
      )}
    </VStack>
  );
};
