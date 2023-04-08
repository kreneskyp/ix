import React from "react";

AgentsListView = () => {
  const [agents, setAgents] = useState([]);
  const AgentsContext = createContext();
  const AgentsProvider = ({ children }) => {
    {
      return (
        <AgentsContext.Provider
          value={{ agents: agents, setAgents: setAgents }}
        >
          {children}
        </AgentsContext.Provider>
      );
    }
  };
  return <div>AgentsListView</div>;
};

export { AgentsListView };
