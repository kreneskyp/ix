import { graphql } from "react-relay/hooks";

export const ChainGraphByIdQuery = graphql`
  query ChainGraphByIdQuery($id: UUID!) {
    graph(id: $id) {
      chain {
        id
        name
        description
        root {
          id
          classPath
          config
          name
          description
        }
      }
      nodes {
        id
        nodeType
        classPath
        config
        name
        description
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
