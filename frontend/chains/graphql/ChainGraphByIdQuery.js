import { graphql } from "react-relay/hooks";

export const ChainGraphByIdQuery = graphql`
  query ChainGraphByIdQuery($id: UUID!) {
    graph(id: $id) {
      chain {
        id
        name
        description
      }
      nodes {
        id
        root
        classPath
        config
        name
        description
        position {
          x
          y
        }
        nodeType {
          id
          name
          description
          classPath
          type
          displayType
          fields
          childField
          connectors {
            key
            type
            sourceType
            multiple
          }
        }
      }
      edges {
        id
        source {
          id
        }
        target {
          id
        }
        key
        inputMap
        relation
      }
    }
  }
`;
