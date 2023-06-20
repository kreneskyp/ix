import { graphql } from "react-relay";

export const SetChainRootMutation = graphql`
  mutation SetChainRootMutation($chainId: UUID!, $nodeId: UUID) {
    setChainRoot(chainId: $chainId, nodeId: $nodeId) {
      old {
        id
        root
      }
      root {
        id
        root
      }
    }
  }
`;
