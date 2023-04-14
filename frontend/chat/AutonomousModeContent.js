import React from "react";
import { Flex, Text } from "@chakra-ui/react";

const AutonomousModeContent = ({ content }) => {
  return (
    <Flex direction="column" mt="4">
      <Text mb="2">
        {content.enabled ? "Enabled" : "Disabled"} autonomous mode.
      </Text>
    </Flex>
  );
};

export default AutonomousModeContent;
