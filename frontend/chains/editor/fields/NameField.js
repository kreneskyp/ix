import React, { useCallback } from "react";
import { FormControl, FormLabel, Input } from "@chakra-ui/react";
import { RequiredAsterisk } from "components/RequiredAsterisk";

export const NameField = ({ object, onChange }) => {
  const handleNameChange = useCallback(
    (e) => {
      onChange({
        ...object,
        name: e.target.value,
      });
    },
    [object, onChange]
  );

  return (
    <FormControl id="name">
      <FormLabel>
        Name <RequiredAsterisk />
      </FormLabel>
      <Input
        type="text"
        placeholder="Enter name"
        value={object?.name || ""}
        onChange={handleNameChange}
      />
    </FormControl>
  );
};
