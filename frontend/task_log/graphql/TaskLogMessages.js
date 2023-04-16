import { graphql } from "relay-runtime";

export const TaskLogMessagesQuery = graphql`
  query TaskLogMessagesQuery($taskId: ID!) {
    taskLogMessages(taskId: $taskId) {
      id
      role
      createdAt
      content {
        __typename
        ... on AssistantContentType {
          type
          thoughts {
            text
            reasoning
            plan
            criticism
            speak
          }
          command {
            name
            args
          }
        }
        ... on AutonomousModeContentType {
          type
          enabled
        }
        ... on AuthorizeContentType {
          type
          messageId
        }
        ... on AuthRequestContentType {
          type
          messageId
        }
        ... on ExecutedContentType {
          type
          messageId
        }
        ... on ExecuteErrorContentType {
          type
          messageId
          errorType
          text
        }
        ... on FeedbackContentType {
          type
          feedback
        }
        ... on FeedbackRequestContentType {
          type
          question
        }
        ... on SystemContentType {
          type
          message
        }
      }
      agent {
        id
        name
      }
    }
  }
`;
