import React, { createContext, useContext } from "react";
import { useFragment, graphql } from "react-relay";

export const AgentContext = createContext(null);

export function AgentProvider({ children, agentId }) {
  const data = useFragment(
    graphql`
      query contexts_agent_Query($id: ID!) {
        agent(id: $id) {
          id
          name
        }
      }
    `,
    { id: agentId }
  );
  return (
    <AgentContext.Provider value={{ agent: data.agent }}>
      {children}
    </AgentContext.Provider>
  );
}

export function useAgent() {
  const context = useContext(AgentContext);
  if (context === null) {
    throw new Error("useAgent must be used within an AgentProvider");
  }
  return context.agent;
}
