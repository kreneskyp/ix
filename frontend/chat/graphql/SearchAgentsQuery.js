import { graphql } from "react-relay/hooks";

export const SearchAgentsQuery = graphql`
  query SearchAgentsQuery($search: String) {
    searchAgents(search: $search) {
      id
      name
      alias
      purpose
      chain {
        id
        name
        description
      }
    }
  }
`;
