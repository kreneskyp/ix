import React from "react";
import { SchemaSelect } from "schemas/SchemaSelect";

export const JSONSchemaSelect = (props) => {
  return <SchemaSelect type={"json"} {...props} />;
};
