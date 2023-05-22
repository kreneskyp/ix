import { graphql } from "react-relay";

export const CreateAgentMutation = graphql`
  mutation AgentMutations_CreateAgentMutation($input: AgentInput!) {
    createAgent(input: $input) {
      agent {
        id
        name
        alias
        model
        purpose
        config
        chain {
          id
          name
        }
      }
    }
  }
`;

export const UpdateAgentMutation = graphql`
  mutation AgentMutations_UpdateAgentMutation($input: AgentInput!) {
    updateAgent(input: $input) {
      agent {
        id
        name
        alias
        purpose
        model
        config
        chain {
          id
          name
        }
      }
    }
  }
`;

export const DeleteAgentMutation = graphql`
  mutation AgentMutations_DeleteAgentMutation($id: UUID!) {
    deleteAgent(id: $id) {
      success
    }
  }
`;
