import React from "react";

export const useOpenAPISchema = (schema_id) => {
  const state = React.useState(null);
  const setSchema = state[1];

  // Effect for fetching data
  React.useEffect(() => {
    const fetchSchema = async () => {
      if (!schema_id) {
        setSchema(null);
        return;
      }

      const response = await fetch("/api/schemas/" + schema_id);
      const data = await response.json();
      setSchema(data);
    };

    fetchSchema();
  }, [schema_id]);
  return state;
};
