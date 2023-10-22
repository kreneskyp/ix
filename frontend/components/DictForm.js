import React from "react";
import {
  Box,
  Input,
  VStack,
  HStack,
  FormLabel,
  Text,
  Tooltip,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTrash, faPlusCircle } from "@fortawesome/free-solid-svg-icons";
import { useEditorColorMode } from "chains/editor/useColorMode";

/**
 * DictForm is a functional component that takes a dictionary and a callback function as props.
 * It renders a form that allows the user to edit the dictionary. The form consists of a list of inputs
 * for each key-value pair in the dictionary, and buttons to add or remove key-value pairs.
 * When a key-value pair is added, removed, or changed, the callback function is called with the new dictionary.
 *
 * @param {Object} dict - The dictionary to be edited.
 * @param {function} onChange - The callback function that is called when the dictionary is changed.
 */
export const DictForm = ({ label, dict, onChange }) => {
  let entries = Object.entries(dict);
  if (entries.length === 0) {
    entries = [["", ""]];
  }
  const colorMode = useEditorColorMode();

  /**
   * Updates the dictionary entries when an input field is changed.
   *
   * @param {Object} e - The event object from the input field.
   * @param {number} index - The index of the key-value pair in the dictionary entries.
   */
  const handleInputChange = (e, index, isKey) => {
    const { value } = e.target;
    const updatedEntries = [...entries];
    updatedEntries[index] = isKey
      ? [value, updatedEntries[index][1]]
      : [updatedEntries[index][0], value];
    onChange(Object.fromEntries(updatedEntries));
  };

  const handleRemoveClick = (index) => {
    const updatedEntries = entries.filter((entry, i) => i !== index);
    onChange(Object.fromEntries(updatedEntries));
  };

  const handleAddClick = () => {
    const updatedEntries = [...entries, ["", ""]];
    onChange(Object.fromEntries(updatedEntries));
  };

  return (
    <Box width="100%">
      <HStack>
        <FormLabel justify="start" whiteSpace="nowrap" mr={0} pr={0}>
          {label}
        </FormLabel>
        <Tooltip label="add value">
          <Text as="span" color={"green.300"}>
            <FontAwesomeIcon
              icon={faPlusCircle}
              onClick={handleAddClick}
              cursor="pointer"
            />
          </Text>
        </Tooltip>
      </HStack>

      <VStack align="stretch">
        {entries.map(([key, value], index) => (
          <HStack key={index}>
            <Input
              value={key}
              onChange={(e) => handleInputChange(e, index, true)}
              placeholder="Key"
              {...colorMode.input}
            />
            <Input
              value={value}
              onChange={(e) => handleInputChange(e, index, false)}
              placeholder="Value"
              {...colorMode.input}
            />
            <FontAwesomeIcon
              icon={faTrash}
              onClick={() => handleRemoveClick(index)}
              cursor="pointer"
            />
          </HStack>
        ))}
      </VStack>
    </Box>
  );
};

export default DictForm;
