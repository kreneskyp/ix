import React from "react";
import { HStack, VStack, Card, CardBody, Heading, Box } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSquareCheck, faClock } from "@fortawesome/free-regular-svg-icons";
import { usePreloadedQuery } from "react-relay/hooks";
import { ChatByIdQuery } from "chat/graphql/ChatByIdQuery";

const SideBarGoalList = ({ queryRef }) => {
  const { chat } = usePreloadedQuery(ChatByIdQuery, queryRef);

  return (
    <VStack spacing={1}>
      <Heading as="h3" size="md" width="100%" align="left" mt={5}>
        Tasks
      </Heading>
      {chat.task.createdPlans?.map((plan, i) => (
        <Box
          bg="transparent"
          color="gray.300"
          _hover={{
            bg: "gray.700",
            cursor: "pointer",
          }}
        >
          <HStack justify="top" py={1} pl={2}>
            <FontAwesomeIcon icon={plan.isComplete ? faSquareCheck : faClock} />
            <span style={{ marginLeft: 10 }}>{plan.name}</span>
          </HStack>
        </Box>
      ))}
    </VStack>
  );
};

export default SideBarGoalList;
