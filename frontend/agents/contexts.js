import React, { createContext, useContext } from "react";
import { useFragment, graphql } from "react-relay";

export const AgentContext = createContext(null);

export function AgentProvider({ children, agentId }) {
  const data = useFragment(
    graphql`
      fragment contexts_agent on Query
      @argumentDefinitions(agentId: { type: "ID!" }) {
        agent(id: $agentId) {
          id
          name
        }
      }
    `,
    { agentId }
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
