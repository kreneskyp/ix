import React from "react";
import { components } from "react-select";
import { OptionContent } from "components/select/Option";

export const SingleValue = (props) => {
  const { getValue } = props;
  const value = getValue()[0];
  return (
    <components.SingleValue {...props}>
      <OptionContent data={value || {}} />
    </components.SingleValue>
  );
};
