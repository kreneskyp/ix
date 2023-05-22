import { graphql } from "react-relay/hooks";

export const AgentByIdQuery = graphql`
  query AgentByIdQuery($id: UUID!) {
    agent(id: $id) {
      id
      name
      alias
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
