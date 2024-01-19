import React from "react";

export const useInputSchema = (schema_id, action) => {
  const state = React.useState(null);
  const setInputSchema = state[1];

  React.useEffect(() => {
    const fetchInputSchema = async () => {
      if (!action) {
        setInputSchema(null);
      } else {
        const { path, method } = action;
        const response = await fetch(
          `/api/schemas/${schema_id}/action?path=${path}&method=${method}`
        );

        if (response.status === 200) {
          const data = await response.json();
          setInputSchema(data);
        } else {
          setInputSchema(null);
          console.warn(
            "Failed to fetch input schema",
            response.status,
            response.statusText
          );
        }
      }
    };
    fetchInputSchema();
  }, [schema_id, action]);

  return state;
};
