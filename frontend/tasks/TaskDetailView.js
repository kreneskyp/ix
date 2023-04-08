import React from react-router-dom import useParams from 'react';

TaskDetailView = () => {
    const { id } = useParams();
    const TaskContext = createContext();
    const TaskProvider = ({ children }) => {{return <TaskContext.Provider value={{ task: task }}>{children}</TaskContext.Provider>}};
    return (
        <div>
            TaskDetailView
        </div>
    )
}

export { TaskDetailView };
