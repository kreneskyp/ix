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
        classPath
        config
        name
        description
        position {
          x
          y
        }
        parent {
          id
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
      }
    }
  }
`;
