import { graphql } from "react-relay/hooks";

export const ChainByIdQuery = graphql`
  query ChainByIdQuery($id: UUID!) {
    chain(id: $id) {
      id
      name
      description
      createdAt
    }
  }
`;
