import { graphql } from "react-relay/hooks";

export const SearchArtifactsQuery = graphql`
  query SearchArtifactsQuery($search: String, $chatId: UUID!) {
    searchArtifacts(search: $search, chatId: $chatId) {
      id
      key
      name
      description
      artifactType
      storage
    }
  }
`;
