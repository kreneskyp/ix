import { graphql } from "react-relay/hooks";

export const AgentByIdQuery = graphql`
  query AgentByIdQuery($id: UUID!) {
    agent(id: $id) {
      id
      name
      model
      purpose
      config
      chain {
        id
        name
        description
      }
    }
  }
`;
