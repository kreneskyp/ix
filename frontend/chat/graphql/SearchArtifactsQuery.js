import { graphql } from "react-relay/hooks";

export const SearchArtifactsQuery = graphql`
  query SearchArtifactsQuery($search: String) {
    searchArtifacts(search: $search) {
      id
      key
      name
      description
      artifactType
      storage
    }
  }
`;
