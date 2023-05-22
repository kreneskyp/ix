import { graphql } from "relay-runtime";

const RemoveAgentMutation = graphql`
  mutation RemoveAgentMutation($chatId: UUID!, $agentId: UUID!) {
    removeAgent(chatId: $chatId, agentId: $agentId) {
      chat {
        id
        agents {
          id
        }
      }
    }
  }
`;

export default RemoveAgentMutation;
