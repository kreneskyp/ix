import React from "react";
import {
  Box,
  Link,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableCaption,
} from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";
import { usePreloadedQuery } from "react-relay/hooks";
import { TasksQuery } from "tasks/graphql/TasksQuery";

export const TasksTable = ({ queryRef }) => {
  const { tasks } = usePreloadedQuery(TasksQuery, queryRef);
  return (
    <Box>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Name</Th>
            <Th>Agent Name</Th>
            <Th>Agent Model</Th>
            <Th>Created</Th>
            <Th>Runtime</Th>
            <Th>Tokens</Th>
            <Th>Cost</Th>
          </Tr>
        </Thead>
        <Tbody>
          {tasks.map((task) => (
            <Tr key={task.id}>
              <Td>
                <Link as={RouterLink} to={`/tasks/chat/${task.id}`}>
                  {task.name}
                </Link>
              </Td>
              <Td></Td>
              <Td></Td>
              <Td>{task.createdAt}</Td>
              <Td></Td>
              <Td></Td>
              <Td></Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};

export default TasksTable;
