import React from "react";
import { HStack, VStack, Text, Heading, Box, Spinner } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faClock } from "@fortawesome/free-regular-svg-icons";
import { faSquareCheck } from "@fortawesome/free-solid-svg-icons";
import { usePreloadedQuery } from "react-relay/hooks";
import { ChatByIdQuery } from "chat/graphql/ChatByIdQuery";

const StatusIcon = ({ isComplete, isRunning }) => {
  if (isComplete) {
    return (
      <Text as="span" color="green.400">
        <FontAwesomeIcon icon={faSquareCheck} />
      </Text>
    );
  } else if (isRunning) {
    return <Spinner size="xs" />;
  }
  return <FontAwesomeIcon icon={faClock} />;
};

const SideBarPlanList = ({ queryRef }) => {
  const { chat } = usePreloadedQuery(ChatByIdQuery, queryRef);
  const { colorMode } = useColorMode();
  return (
    <VStack spacing={1}>
      <Heading as="h3" size="md" width="100%" align="left" mt={5}>
        Tasks
      </Heading>
      {chat.task.createdPlans?.length === 0 ? (
          <Text
              p={2}
              fontSize="xs"
              color="gray.400"
              sx={{borderRadius: "5px"}}
          >
            Task plans for your requests will appear here as they are created by agents.
          </Text>
      ) : null}
      {chat.task.createdPlans?.map((plan, i) => (
        <Box
          key={i}
          bg="transparent"
          color={colorMode === "light" ? "gray.700" : "gray.400"}
          _hover={{
            bg: colorMode === "light" ? "gray.300" : "gray.700",
            cursor: "pointer",
          }}
        >
          <HStack justify="top" py={1} pl={2} width="100%">
            <StatusIcon
              isComplete={plan.isComplete}
              isRunning={plan.task !== undefined}
            />
            <span style={{ marginLeft: 10 }}>{plan.name}</span>
          </HStack>
        </Box>
      ))}
    </VStack>
  );
};

export default SideBarPlanList;
