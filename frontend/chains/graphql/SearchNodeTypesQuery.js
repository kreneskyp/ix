import { graphql } from "react-relay/hooks";

export const SearchNodeTypesQuery = graphql`
  query SearchNodeTypesQuery($search: String) {
    searchNodeTypes(search: $search) {
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
