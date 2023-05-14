import { graphql } from "react-relay";

export const AddAgentMutation = graphql`
  mutation AddAgentMutation($chatId: UUID!, $agentId: UUID!) {
    addAgent(chatId: $chatId, agentId: $agentId) {
      chat {
        id
        agents {
          id
        }
      }
    }
  }
`;
