import { graphql } from "react-relay";

export const CreateAgentMutation = graphql`
  mutation AgentMutations_CreateAgentMutation($input: AgentInput!) {
    createAgent(input: $input) {
      agent {
        id
        name
        model
        config
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
        model
        config
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
