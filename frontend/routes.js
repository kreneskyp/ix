import React from "react";

import { TasksListView } from "tasks/TasksListView";
import { TaskLogView } from "task_log/TaskLogView";
import { AgentEditorView } from "agents/AgentEditorView";
import { AgentsListView } from "agents/AgentsListView";
import { ChatView } from "chat/ChatView";
import { ChainListView } from "chains/ChainListView";
import { ChainEditorView } from "chains/ChainEditorView";
import { NewChatRedirect } from "chat/NewChatRedirect";
import { ChatHistoryView } from "chat/history/ChatHistoryView";
//import { UserSettingsView } from 'users/UserSettingsView';
//import { AdminSettingsView } from 'admin/AdminSettingsView';

export const routes = [
  { path: "/proto", element: <ChainEditorView /> },
  { path: "/proto/:id", element: <ChainEditorView /> },
  { path: "/tasks", element: <TasksListView /> },
  { path: "/chats/new", element: <NewChatRedirect /> },
  {
    path: "/tasks/chat/:id",
    element: <TaskLogView />,
  },
  {
    path: "/chat/:id",
    element: <ChatView />,
  },
  { path: "/chats", element: <ChatHistoryView /> },
  { path: "/chains", element: <ChainListView /> },
  { path: "/chains/new", element: <ChainEditorView /> },
  { path: "/chains/:id", element: <ChainEditorView /> },
  { path: "/agents", element: <AgentsListView /> },
  { path: "/agents/new", element: <AgentEditorView /> },
  { path: "/agents/:id", element: <AgentEditorView /> },
  { path: "*", element: <NewChatRedirect /> },
];

export default routes;
