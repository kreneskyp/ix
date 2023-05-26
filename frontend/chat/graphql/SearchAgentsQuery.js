import { graphql } from "react-relay/hooks";

export const SearchAgentsQuery = graphql`
  query SearchAgentsQuery($search: String, $chatId: UUID) {
    searchAgents(search: $search, chatId: $chatId) {
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
