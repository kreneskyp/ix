import React from "react";
import { Box, FormLabel, FormHelperText } from "@chakra-ui/react";
import { getLabel } from "json_form/utils";

/**
 * Generic JSONSchemaForm field component that wraps a Select component. This is a
 * shortcut for adding integrating a custom component with JSONSchemaForm.
 */
export const APISelect = ({
  Component,
  name,
  field,
  isRequired,
  config,
  value,
  onChange,
}) => {
  const handleChange = React.useCallback(
    (value) => {
      onChange({ [name]: value });
    },
    [field, onChange]
  );

  return (
    <Box width="100%" justifyItems={"start"}>
      <FormLabel size="sm" justify="start">
        {getLabel(field.label || name)}
      </FormLabel>
      <Component
        onConfigChange={onChange}
        onChange={handleChange}
        config={config}
        value={value}
        width={"100%"}
      />
      <FormHelperText fontSize={"xs"}>{field.description}</FormHelperText>
    </Box>
  );
};

/**
 * Helper for composing a custom APISelect component for JSONSchemaForm.
 * @param component
 * @returns {function(*): *}
 */
APISelect.for_select = (component) => {
  return (props) => {
    return <APISelect Component={component} {...props} />;
  };
};
