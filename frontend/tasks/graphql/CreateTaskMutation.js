import { graphql } from "react-relay";

export const CreateTaskMutation = graphql`
  mutation CreateTaskMutation($input: CreateTaskInput!) {
    createTask(input: $input) {
      task {
        id
        name
        agent {
          id
          name
          purpose
        }
        goals {
          description
        }
      }
    }
  }
`;
