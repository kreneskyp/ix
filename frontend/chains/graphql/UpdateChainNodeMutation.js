import { graphql } from "react-relay";

export const UpdateChainNodeMutation = graphql`
  mutation UpdateChainNodeMutation($data: ChainNodeInput!) {
    updateChainNode(data: $data) {
      node {
        id
        classPath
        config
        name
        description
        position {
          x
          y
        }
      }
    }
  }
`;
