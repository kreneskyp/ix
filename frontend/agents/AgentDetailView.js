import React from react-router-dom import useParams from 'react';

const AgentDetailView = () => {
    const { id } = useParams();
    const AgentContext = createContext();
    const AgentProvider = ({ children }) => {{return <AgentContext.Provider value={{ agent: agent }}>{children}</AgentContext.Provider>}};
    return (
        <div>
            AgentDetailView
        </div>
    )
}

export { AgentDetailView };
