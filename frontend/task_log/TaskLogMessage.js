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
          <Text>{message?.agent?.name}</Text>
          <Text>{message?.role}</Text>
          <Text fontWeight="bold">Timestamp:</Text>
          <Text>{message.createdAt}</Text>
          <Text fontWeight="bold">Content:</Text>
          <Text>{message.content}</Text>
        </Grid>
      </CardBody>
    </Card>
  );
};

export default TaskLogMessage;
