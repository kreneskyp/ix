import React from "react";
import { Box, FormLabel } from "@chakra-ui/react";
import { getLabel } from "json_form/utils";
import { SecretSelect as _SecretSelect } from "secrets/SecretSelect";

/**
 * JSONSchemaForm's SecretSelect wraps SecretSelect to map that secret to a
 * a group of fields in the JSONSchema.
 */
export const SecretSelect = ({ name, field, isRequired, config, onChange }) => {
  // all properties in the secret group should have the same value.
  const value = config[field.properties[0]];

  const handleChange = React.useCallback(
    (event) => {
      // update all properties in the secret group.
      const data = {};
      for (const key of field.properties) {
        console.log("updating key: ", key, event.target.value);
        data[key] = event.target.value;
      }
      onChange(data);
    },
    [field]
  );

  return (
    <Box width="100%" justifyItems={"start"}>
      <FormLabel size="sm" justify="start">
        {getLabel(name)}
      </FormLabel>
      <_SecretSelect
        secretKey={name}
        onChange={handleChange}
        value={value}
        width={"100%"}
      />
    </Box>
  );
};
