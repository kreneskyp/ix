import { graphql } from "react-relay";

export const DeleteChainEdgeMutation = graphql`
  mutation DeleteChainEdgeMutation($id: UUID!) {
    deleteChainEdge(id: $id) {
      id
    }
  }
`;
