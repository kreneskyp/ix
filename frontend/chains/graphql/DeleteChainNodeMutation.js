import { graphql } from "react-relay";

export const DeleteChainNodeMutation = graphql`
  mutation DeleteChainNodeMutation($id: UUID!) {
    deleteChainNode(id: $id) {
      node {
        id
      }
      edges {
        id
      }
    }
  }
`;
