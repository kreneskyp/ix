// UserContext.js
import React, { createContext, useContext } from "react";
import { useFragment, graphql } from "react-relay";

export const UserContext = createContext(null);
export const UsersContext = createContext(null);

export function UsersProvider({ children }) {
  const data = useFragment(
    graphql`
      fragment contexts_users on Query {
        users {
          id
          username
          email
          first_name
          last_name
        }
      }
    `,
    null
  );
  return (
    <UsersContext.Provider value={{ users: data.users }}>
      {children}
    </UsersContext.Provider>
  );
}

export function useUsers() {
  const context = useContext(UsersContext);
  if (context === null) {
    throw new Error("useUsers must be used within a UsersProvider");
  }
  return context.users;
}

export function UserProvider({ children, userId }) {
  const data = useFragment(
    graphql`
      fragment contexts_user on Query
      @argumentDefinitions(userId: { type: "ID!" }) {
        user(id: $userId) {
          id
          username
          email
          first_name
          last_name
        }
      }
    `,
    { userId }
  );
  return (
    <UserContext.Provider value={{ user: data.user }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === null) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return context.user;
}
