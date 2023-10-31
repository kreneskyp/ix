import React from "react";
import { DictForm } from "components/DictForm";
import { getLabel } from "json_form/utils";

export const Dict = ({ name, field, isRequired, value, onChange }) => {
  const handleChange = React.useCallback(
    (newValue) => {
      // Check if newValue is null or undefined, if so, set it to an empty object
      newValue = newValue || {};
      onChange({ [name]: newValue });
    },
    [field, onChange]
  );

  // Check if value is null or undefined, if so, set it to an empty object
  value = value || {};

  return (
    <DictForm
      dict={value}
      onChange={handleChange}
      label={getLabel(name)}
      isRequired
    />
  );
};
