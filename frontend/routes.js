import React from "react";

import { TasksListView } from "tasks/TasksListView";
import { ChatView } from "chat/ChatView";
import { ChainEditorView } from "chains/ChainEditorView";
import { NewChatRedirect } from "chat/NewChatRedirect";
import { ChatHistoryView } from "chat/history/ChatHistoryView";
import { AgentEditorRedirect } from "agents/AgentEditorRedirect";
import { AgentNewRedirect } from "agents/AgentNewRedirect";
//import { UserSettingsView } from 'users/UserSettingsView';
//import { AdminSettingsView } from 'admin/AdminSettingsView';

export const routes = [
  { path: "/tasks", element: <TasksListView /> },
  { path: "/chats/new", element: <NewChatRedirect /> },
  {
    path: "/chat/:id",
    element: <ChatView />,
  },
  { path: "/chats", element: <ChatHistoryView /> },
  { path: "/chains", element: <ChainEditorView /> },
  { path: "/chains/:id", element: <ChainEditorView /> },
  { path: "/agents/new", element: <AgentNewRedirect /> },
  { path: "/agents/:id", element: <AgentEditorRedirect /> },
  { path: "*", element: <NewChatRedirect /> },
];

export default routes;
