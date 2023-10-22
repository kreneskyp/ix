import React from "react";
import SliderInput from "components/SliderInput";
import { getLabel } from "json_form/utils";
export const Slider = ({ name, field, value, onChange }) => {
  const handleChange = React.useCallback(
    (newValue) => {
      onChange(name, newValue);
    },
    [field, onChange]
  );

  return (
    <SliderInput
      label={getLabel(name)}
      field={name}
      value={value}
      onChange={handleChange}
      min={field.minimum}
      max={field.maximum}
      step={field.multipleOf}
    />
  );
};
