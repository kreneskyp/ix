import React from "react";
import { graphql } from "relay-runtime";

export const NodeTypesQuery = graphql`
  query NodeTypesQuery {
    nodeTypes {
      id
      name
      description
      classPath
      type
      displayType
      connectors {
        key
        type
        sourceType
        multiple
      }
      fields
      childField
    }
  }
`;
