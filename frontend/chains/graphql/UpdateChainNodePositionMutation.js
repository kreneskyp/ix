import { graphql } from "react-relay";

export const UpdateChainNodePositionMutation = graphql`
  mutation UpdateChainNodePositionMutation($data: ChainNodePositionInput!) {
    updateChainNodePosition(data: $data) {
      node {
        id
        position {
          x
          y
        }
      }
    }
  }
`;
