import React from "react";
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Tooltip,
  Box,
} from "@chakra-ui/react";
import { CheckIcon, WarningIcon, TimeIcon } from "@chakra-ui/icons";
import { Link } from "react-router-dom";
import { useTasks } from "tasks/contexts";
import { useLatestTaskLog } from "task_log/contexts";

const TasksTable = () => {
  const tasks = useTasks();
  let rows;
  if (tasks) {
    rows = tasks.map((task) => <TaskRow key={task.id} task={task} />);
  }

  return (
    <Table variant="striped" colorScheme="gray">
      <Thead>
        <Tr>
          <Th>Title</Th>
          <Th>User</Th>
          <Th>Status</Th>
        </Tr>
      </Thead>
      <Tbody>{rows}</Tbody>
    </Table>
  );
};

const TaskRow = ({ task }) => {
  const latestTaskLog = useLatestTaskLog(task.id);

  let statusIcon = null;
  if (task.is_complete) {
    statusIcon = <CheckIcon color="green.500" />;
  } else if (
    latestTaskLog &&
    latestTaskLog.assistant_response &&
    !latestTaskLog.user_response
  ) {
    statusIcon = (
      <Tooltip label="Waiting for user input">
        <Box as="span" color="gray.500">
          <TimeIcon />
        </Box>
      </Tooltip>
    );
  } else if (latestTaskLog && latestTaskLog.error_message) {
    statusIcon = (
      <Tooltip label={latestTaskLog.error_message}>
        <Box as="span" color="red.500">
          <WarningIcon />
        </Box>
      </Tooltip>
    );
  } else {
    statusIcon = (
      <Tooltip label="Running">
        <Box as="span" color="yellow.500">
          <TimeIcon />
        </Box>
      </Tooltip>
    );
  }

  return (
    <Tr>
      <Td>
        <Link to={`/tasks/chat/${task.id}`}>{task.id}</Link>
      </Td>
      <Td>{statusIcon}</Td>
    </Tr>
  );
};

export default TasksTable;
