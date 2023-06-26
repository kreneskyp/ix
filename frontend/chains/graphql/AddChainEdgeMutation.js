import { graphql } from "react-relay";

export const AddChainEdgeMutation = graphql`
  mutation AddChainEdgeMutation($data: ChainEdgeInput!) {
    addChainEdge(data: $data) {
      edge {
        id
        key
        inputMap
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
