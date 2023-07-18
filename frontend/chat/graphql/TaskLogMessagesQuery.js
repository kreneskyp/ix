import { graphql } from "relay-runtime";

export const TaskLogMessagesQuery = graphql`
  query TaskLogMessagesQuery($taskId: UUID!) {
    taskLogMessages(taskId: $taskId) {
      id
      role
      createdAt
      parent {
        id
      }
      content
      agent {
        id
        name
      }
    }
  }
`;
