import { graphql } from "react-relay";

export const UpdateChainMutation = graphql`
  mutation UpdateChainMutation($data: ChainInput!) {
    updateChain(data: $data) {
      chain {
        id
        name
        description
      }
    }
  }
`;
