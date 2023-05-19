import React from "react";
import { Table, Thead, Tbody, Tr, Th, Td } from "@chakra-ui/react";
import { Link } from "react-router-dom";
import { ChatHistoryQuery } from "chat/graphql/ChatHistoryQuery";
import { usePreloadedQuery } from "react-relay/hooks";
import { Pagination } from "components/Pagination";

export const ChatTable = ({ queryRef, load }) => {
  const { chatPage } = usePreloadedQuery(ChatHistoryQuery, queryRef);
  const { count, hasNext, hasPrevious, objects, pages, pageNumber } = chatPage;
  const chats = objects;

  return (
    <div>
      <Table colorScheme="gray" mb={10}>
        <Thead>
          <Tr>
            <Th>Name</Th>
            <Th>Created At</Th>
            <Th>Agents</Th>
          </Tr>
        </Thead>
        <Tbody>
          {chats?.map((chat) => {
            const { id, name } = chat;
            const chatLink = `/chat/${id}`;
            const createdAt = new Date(chat.createdAt).toLocaleString();

            return (
              <Tr key={id}>
                <Td>
                  <Link to={chatLink}>{name || createdAt}</Link>
                </Td>
                <Td>{createdAt}</Td>
                <Td>
                  {chat.agents.map((agent) => (
                    <span>{agent.alias} </span>
                  ))}
                </Td>
              </Tr>
            );
          })}
        </Tbody>
      </Table>
      <Pagination
        hasNext={hasNext}
        hasPrevious={hasPrevious}
        load={load}
        pages={pages}
        pageNumber={pageNumber}
      />
    </div>
  );
};
