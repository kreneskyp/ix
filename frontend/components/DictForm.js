import React from "react";
import { Box, Button, Input, VStack, HStack } from "@chakra-ui/react";

const DictForm = ({ dict, onChange }) => {
  const entries = Object.entries(dict);

  const handleInputChange = (e, index) => {
    const { name, value } = e.target;
    const updatedEntries = [...entries];
    updatedEntries[index] = [name, value];
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
    <VStack align="stretch">
      {entries.map(([key, value], index) => (
        <HStack key={index}>
          <Input
            value={key}
            name="key"
            onChange={(e) => handleInputChange(e, index)}
            placeholder="Key"
          />
          <Input
            value={value}
            name="value"
            onChange={(e) => handleInputChange(e, index)}
            placeholder="Value"
          />
          <Button colorScheme="red" onClick={() => handleRemoveClick(index)}>
            Remove
          </Button>
        </HStack>
      ))}
      <Button colorScheme="teal" onClick={handleAddClick}>
        Add
      </Button>
    </VStack>
  );
};

export default DictForm;
