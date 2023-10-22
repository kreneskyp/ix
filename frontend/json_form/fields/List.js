import React from "react";
import { ListForm } from "components/ListForm";
import { getLabel } from "json_form/utils";

export const List = ({ name, field, isRequired, value, onChange }) => {
  const handleChange = React.useCallback(
    (newValue) => {
      // Check if newValue is null or undefined, if so, set it to an empty array
      newValue = newValue || [];
      onChange(name, newValue);
    },
    [field, onChange]
  );

  // Check if value is null or undefined, if so, set it to an empty array
  value = value || [];

  return (
    <ListForm
      list={value}
      onChange={handleChange}
      label={getLabel(name)}
      isRequired
    />
  );
};
