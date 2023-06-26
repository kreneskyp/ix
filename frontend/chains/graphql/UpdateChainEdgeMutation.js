import { graphql } from "react-relay";

export const UpdateChainEdgeMutation = graphql`
  mutation UpdateChainEdgeMutation($data: ChainEdgeInput!) {
    updateChainEdge(data: $data) {
      edge {
        id
        inputMap
        key
        source {
          id
        }
        target {
          id
        }
      }
    }
  }
`;
