import React from "react";
import { graphql } from "relay-runtime";

export const TasksQuery = graphql`
  query TasksQuery {
    tasks {
      id
      name
      createdAt
      isComplete
      completeAt
      goals {
        description
        complete
      }
      agent {
        id
        name
        model
      }
    }
    
  }
`;
