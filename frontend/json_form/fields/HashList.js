import React from "react";
import { getLabel } from "json_form/utils";
import HashListForm from "components/HashListForm";

export const HashList = ({
  name,
  field,
  isRequired,
  config,
  onChange,
  onDelete,
  defaultValue,
  component,
}) => {
  const hashField = `${name}_hash`;

  const handleChange = React.useCallback(
    (newValue) => {
      const updatedFields = {
        [name]: newValue.list,
        [hashField]: newValue.hash_list,
      };
      onChange(updatedFields);
    },
    [field, onChange]
  );

  return (
    <HashListForm
      list={config[name]}
      hash_list={config[hashField]}
      onChange={handleChange}
      onDelete={onDelete}
      label={getLabel(name)}
      isRequired
      defaultValue={defaultValue}
      component={component}
    />
  );
};
