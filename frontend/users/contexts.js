import React, { createContext, useContext } from "react";
import { useFragment, graphql } from "react-relay";

export const UserContext = createContext(null);
export const UsersContext = createContext(null);

export function UsersProvider({ children }) {
  const data = useFragment(
    graphql`
      query contexts_users_Query {
        users {
          id
          username
          email
          firstName
          lastName
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
      query contexts_user_Query ($id: ID!) {
        user(id: $id) {
          id
          username
          email
          firstName
          lastName
        }
      }
    `,
    { id: userId }
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
