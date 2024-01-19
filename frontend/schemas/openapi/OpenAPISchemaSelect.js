import React from "react";
import { SchemaSelect } from "schemas/SchemaSelect";

export const OpenAPISchemaSelect = (props) => {
  return <SchemaSelect type={"openapi"} {...props} />;
};
