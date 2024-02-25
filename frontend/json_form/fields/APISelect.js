import React from "react";
import { Box, FormLabel, FormHelperText } from "@chakra-ui/react";
import { getLabel } from "json_form/utils";

export const DefaultHelp = ({ field }) => (
  <FormHelperText fontSize={"xs"}>{field.description}</FormHelperText>
);

/**
 * Generic JSONSchemaForm field component that wraps a Select component. This is a
 * shortcut for adding integrating a custom component with JSONSchemaForm.
 */
export const APISelect = ({
  Component,
  HelpComponent,
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
      <HelpComponent field={field} value={value} config={config} />
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
    return (
      <APISelect
        Component={component}
        HelpComponent={component.help || DefaultHelp}
        {...props}
      />
    );
  };
};

APISelect.defaultProps = {
  HelpComponent: DefaultHelp,
};
