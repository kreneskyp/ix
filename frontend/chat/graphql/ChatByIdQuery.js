import { graphql } from "react-relay/hooks";

export const ChatByIdQuery = graphql`
  query ChatByIdQuery($id: UUID!) {
    chat(id: $id) {
      id
      name
      lead {
        id
        name
        alias
        purpose
        createdAt
        model
        config
        chain {
          id
        }
      }
      agents {
        id
        name
        alias
        purpose
        createdAt
        model
        config
        chain {
          id
        }
      }

      task {
        id
        createdPlans(isDraft: false) {
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
        artifacts {
          id
          name
          key
          description
          artifactType
          storage
          createdAt
        }
      }
    }
  }
`;
