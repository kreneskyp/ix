import React, { useState, useEffect } from "react";
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
 * ListForm is a functional component that takes a list and a callback function as props.
 * It renders a form that allows the user to edit the list. The form consists of a list of inputs
 * for each item in the list, and buttons to add or remove items.
 * When an item is added, removed, or changed, the callback function is called with the new list.
 *
 * @param {Array} list - The list to be edited.
 * @param {function} onChange - The callback function that is called when the list is changed.
 */
export const ListForm = ({ label, list, onChange }) => {
  const [items, setItems] = useState(list || [""]);
  const colorMode = useEditorColorMode();

  // This useEffect hook ensures that there is always an empty string at the end of the items array.
  // This is necessary for the user to be able to add new items to the list.
  useEffect(() => {
    if (items[items.length - 1] !== "") {
      setItems([...items, ""]);
    }
  }, [items]);

  /**
   * Updates the list items when an input field is changed.
   *
   * @param {Object} e - The event object from the input field.
   * @param {number} index - The index of the item in the list.
   */
  const handleInputChange = (e, index) => {
    const { value } = e.target;
    const updatedItems = [...items];
    updatedItems[index] = value;
    setItems(updatedItems);
    onChange(updatedItems.filter((item) => item !== ""));
  };

  const handleRemoveClick = (index) => {
    const updatedItems = items.filter((item, i) => i !== index);
    setItems(updatedItems);
    onChange(updatedItems.filter((item) => item !== ""));
  };

  return (
    <Box width="100%">
      <HStack>
        <FormLabel justify="start" whiteSpace="nowrap" mr={0} pr={0}>
          {label}
        </FormLabel>
      </HStack>

      <VStack align="stretch">
        {items.map((value, index) => (
          <HStack key={index}>
            <Input
              value={value}
              onChange={(e) => handleInputChange(e, index)}
              placeholder={`Item ${index + 1}`}
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

export default ListForm;
