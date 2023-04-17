import { Button, Text, VStack } from "@chakra-ui/react";
import React from "react";

export const AgentResourceEditor = ({ agent }) => {
  return (
    <VStack spacing={4}>
      <Text>Resource management UI</Text>
      <Button onClick={null}>Create Resource</Button>
      <Button onClick={null}>Update Resource</Button>
      <Button onClick={null}>Delete Resource</Button>
    </VStack>
  );
};
