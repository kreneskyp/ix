import React, { Suspense } from "react";
import { Navigate } from "react-router-dom";

import { TasksListView } from "tasks/TasksListView";
//import { TaskDetailView } from 'tasks/TaskDetailView';
import { TaskLogView } from "task_log/TaskLogView";
//import { AgentsListView } from 'agents/AgentsListView';
//import { AgentDetailView } from 'agents/AgentDetailView';
//import { TaskLogView } from 'task_log/TaskLogView';
//import { UserSettingsView } from 'users/UserSettingsView';
//import { AdminSettingsView } from 'admin/AdminSettingsView';

export const routes = [
  { path: "/tasks", element: <TasksListView /> },
  { path: "/tasks/chat", element: <TaskLogView /> },
  {
    path: "/tasks/chat/:id",
    element: (
      <Suspense fallback={<div>Loading!</div>}>
        <TaskLogView />
      </Suspense>
    ),
  },
  { path: "*", element: <TasksListView /> },
];

//  <Route exact path='/tasks/:id' component={TaskDetailView} />
//        <Route exact path='/agents' component={AgentsListView} />
//        <Route exact path='/agents/:id' component={AgentDetailView} />
//        <Route exact path='/task_log/:taskId' component={TaskLogView} />
//        <Route exact path='/users/settings' component={UserSettingsView} />
//        <Route exact path='/admin/settings' component={AdminSettingsView} />

export default routes;
