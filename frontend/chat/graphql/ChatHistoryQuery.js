import { graphql } from "react-relay";

export const ChatHistoryQuery = graphql`
  query ChatHistoryQuery($limit: Int, $offset: Int) {
    chatPage(limit: $limit, offset: $offset) {
      pageNumber
      pages
      count
      hasNext
      hasPrevious
      objects {
        id
        name
        createdAt
        agents {
          id
          alias
        }
      }
    }
  }
`;
