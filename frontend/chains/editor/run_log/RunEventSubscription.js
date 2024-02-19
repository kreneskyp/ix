import { graphql } from "react-relay";

export const RunEventSubscription = graphql`
  subscription RunEventSubscription($chainId: String) {
    runEventSubscription(chainId: $chainId) {
      event {
        __typename
        ... on ExecutionType {
          id
          parentId
          nodeId
          startedAt
          finishedAt
          completed
          inputs
          outputs
          message
        }
        ... on RunStartType {
          taskId
        }
      }
    }
  }
`;
