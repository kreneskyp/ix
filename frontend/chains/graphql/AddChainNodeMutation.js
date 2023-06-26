import { graphql } from "react-relay";

export const AddChainNodeMutation = graphql`
  mutation AddChainNodeMutation($data: ChainNodeInput!) {
    addChainNode(data: $data) {
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
        chain {
          id
        }
      }
    }
  }
`;
