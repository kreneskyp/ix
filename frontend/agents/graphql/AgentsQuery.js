import React from "react";
import { graphql } from "relay-runtime";

export const AgentsQuery = graphql`
  query AgentsQuery {
    agents {
      id
      name
      alias
      model
      config
      chain {
        id
        name
        description
      }
    }
  }
`;
