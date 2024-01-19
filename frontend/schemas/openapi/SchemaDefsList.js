import React from "react";
import { Box } from "@chakra-ui/react";
import { CollapsibleSection } from "chains/flow/CollapsibleSection";
import { JSONSchemaDisplay } from "schemas/json/JSONSchemaDisplay";

export const SchemaDefsList = ({ schema }) => {
  const definitions = schema.components?.schemas;
  return (
    <Box>
      {Object.keys(definitions).map((name) => (
        <CollapsibleSection key={name} title={name} mb={2}>
          <JSONSchemaDisplay schema={definitions[name]} />
        </CollapsibleSection>
      ))}
    </Box>
  );
};

export default SchemaDefsList;
