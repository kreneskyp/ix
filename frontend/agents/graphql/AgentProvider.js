import React, { createContext, useContext, useState, useEffect } from "react";
import { useLazyLoadQuery, usePreloadedQuery } from "react-relay/hooks";
import { graphql } from "react-relay";

const AgentContext = createContext();

export const AgentProvider = ({ agentId, children }) => {
  const data = useLazyLoadQuery(
    graphql`
      query AgentProvider_AgentByIdQuery($id: ID!) {
        agent: agent(id: $id) {
          id
          name
          model
          purpose
          systemPrompt
          commands
          config
        }
      }
    `,
    { id: agentId }
  );

  const [agent, setAgent] = useState();

  useEffect(() => {
    if (data && data.agent) {
      setAgent(data.agent);
    }
  }, [data]);

  return (
    <AgentContext.Provider value={{ agent, setAgent }}>
      {children}
    </AgentContext.Provider>
  );
};

export const useAgent = () => {
  const context = useContext(AgentContext);
  if (context === undefined) {
    throw new Error("useAgent must be used within an AgentProvider");
  }
  return context;
};
