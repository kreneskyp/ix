import { graphql } from "react-relay/hooks";

export const ChatByIdQuery = graphql`
  query ChatByIdQuery($id: UUID!) {
    chat(id: $id) {
      id
      name
      lead {
        id
        name
        purpose
        createdAt
        model
      }
      agents {
        id
        name
        purpose
        createdAt
        model
      }
      artifacts {
        id
        name
        key
        description
        reference
      }
      task {
        id
        createdPlans {
          id
          name
          description
          createdAt
          isDraft
          isComplete
          steps {
            id
            isComplete
            details
          }
          runner {
            id
          }
        }
      }
    }
  }
`;
