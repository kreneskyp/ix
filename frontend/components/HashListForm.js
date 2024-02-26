import React from "react";
import { v4 as uuidv4 } from "uuid";
import { Box, Input, VStack, HStack, FormLabel } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTrash } from "@fortawesome/free-solid-svg-icons";
import { useEditorColorMode } from "chains/editor/useColorMode";

/**
 * HashListForm is a functional component that takes an object with list and hash_list as props.
 * It renders a form that allows the user to edit the list with corresponding UUIDs.
 */
export const HashListForm = ({
  label,
  list,
  hash_list,
  onChange,
  onDelete,
  component,
  defaultValue,
}) => {
  const colorMode = useEditorColorMode();
  const _defaultValue = defaultValue || "";

  const handleInputChange = (e, index) => {
    const { value } = e.target;
    const updatedItems = [...(list || [])];
    const updatedHashes = [...(hash_list || [])];

    if (index < list?.length || 0) {
      updatedItems[index] = value;
    } else {
      updatedItems.push(value);
      updatedHashes.push(uuidv4());
    }

    onChange({
      list: updatedItems,
      hash_list: updatedHashes,
    });
  };

  const handleRemoveClick = (index) => {
    onChange({
      list: list.filter((item, i) => i !== index),
      hash_list: hash_list.filter((hash, i) => i !== index),
    });
    onDelete(hash_list[index], list[index]);
  };

  // Add empty element here so the rendered structure and input focus sticks
  // while typing in the new item.
  const list_plus_new = list ? [...list, _defaultValue] : [_defaultValue];
  const InputComponent = component || Input;

  return (
    <Box width="100%">
      <FormLabel>{label}</FormLabel>
      <VStack align="stretch">
        {list_plus_new?.map((value, index) => (
          <HStack key={index}>
            <InputComponent
              value={value}
              onChange={(e) => handleInputChange(e, index)}
              placeholder={`Item ${index + 1}`}
              {...colorMode.input}
            />
            <FontAwesomeIcon
              icon={faTrash}
              onClick={() => handleRemoveClick(index)}
              cursor={index < list?.length ? "pointer" : "default"}
              color={index < list?.length ? "inherit" : "transparent"}
            />
          </HStack>
        ))}
      </VStack>
    </Box>
  );
};

export default HashListForm;
