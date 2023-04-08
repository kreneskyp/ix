import React from "react";
import { Card, CardBody, Grid, Text } from "@chakra-ui/react";

export const TaskLogMessage = ({ message }) => {
  return (
    <Card>
      <CardBody>
        <Grid
          templateColumns="repeat(2, auto)"
          gap={2}
          alignItems="center"
          mb={2}
        >
          <Text fontWeight="bold">Agent:</Text>
          <Text>{message.agent.name}</Text>
          <Text fontWeight="bold">Timestamp:</Text>
          <Text>{message.assistantTimestamp}</Text>
          <Text fontWeight="bold">Command:</Text>
          <Text>{message.command}</Text>
          <Text fontWeight="bold">UserResponseAt:</Text>
          <Text>{message.userTimestamp}</Text>
          <Text fontWeight="bold">User Response</Text>
          <Text>{message.userResponse}</Text>
        </Grid>
      </CardBody>
    </Card>
  );
};

export default TaskLogMessage;
