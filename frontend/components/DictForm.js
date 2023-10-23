import React, { useEffect, useState } from "react";
import { Box, Input, VStack, HStack, FormLabel, Text } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTrash } from "@fortawesome/free-solid-svg-icons";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { useDebounce } from "utils/hooks/useDebounce";

export const DictForm = ({ label, dict, onChange }) => {
  const [entries, setEntries] = useState(() => {
    let entries = Object.entries(dict);
    if (entries.length === 0) {
      entries = [["", ""]];
    } else {
      // Move entries with empty keys to the end
      entries.sort(([keyA], [keyB]) =>
        keyA === "" ? 1 : keyB === "" ? -1 : 0
      );
    }
    return entries;
  });
  const colorMode = useEditorColorMode();

  const handleInputChange = (e, index, isKey) => {
    const { value } = e.target;
    const updatedEntries = [...entries];
    updatedEntries[index] = isKey
      ? [value, updatedEntries[index][1]]
      : [updatedEntries[index][0], value];

    // Update local state immediately for quick feedback to the user
    setEntries(updatedEntries);
  };

  // This effect will update the parent component when entries change
  useEffect(() => {
    if (entries) {
      const filteredEntries = entries.filter(([key]) => key !== "");
      onChange(Object.fromEntries(filteredEntries));
    }

    // Check if the last entry is empty before adding a new one
    if (entries[entries.length - 1].some((entry) => entry !== "")) {
      setEntries([...entries, ["", ""]]); // Adds a new entry line immediately
    }
  }, [entries]);

  const handleRemoveClick = (index) => {
    const updatedEntries = [...entries];
    updatedEntries.splice(index, 1);
    setEntries(updatedEntries);
  };

  return (
    <Box width="100%">
      <HStack>
        <FormLabel justify="start" whiteSpace="nowrap" mr={0} pr={0}>
          {label}
        </FormLabel>
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
