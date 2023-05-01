import React from "react";
import { graphql } from "relay-runtime";

export const ChainsQuery = graphql`
  query ChainsQuery {
    chains {
      id
      name
      description
    }
  }
`;
