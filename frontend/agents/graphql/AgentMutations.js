import { graphql } from "react-relay";

export const CreateAgentMutation = graphql`
  mutation AgentMutations_CreateAgentMutation($input: AgentInput!) {
    createAgent(input: $input) {
      agent {
        id
        name
        model
        systemPrompt
        commands
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
        systemPrompt
        commands
        config
      }
    }
  }
`;

export const DeleteAgentMutation = graphql`
  mutation AgentMutations_DeleteAgentMutation($id: ID!) {
    deleteAgent(id: $id) {
      success
    }
  }
`;
