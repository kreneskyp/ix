import React from "react";

export const useOpenAPIActions = (schema) => {
  // convert schema paths into actions
  return React.useMemo(() => {
    if (!schema) return null;

    const actions = [];

    try {
      Object.keys(schema.paths || []).forEach((path) => {
        const pathItem = schema.paths[path];
        Object.keys(pathItem).forEach((method) => {
          const operation = pathItem[method];
          const action = {
            path,
            method,
            operation,
          };
          actions.push(action);
        });
      });
    } catch (e) {
      console.error("Error parsing OpenAPI schema: ", e);
    }

    return actions;
  }, [schema]);
};
