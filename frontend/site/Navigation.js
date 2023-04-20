import React from "react";
import { Box, Flex, HStack, Stack } from "@chakra-ui/react";
import {
  faCog,
  faSignOutAlt,
  faRobot,
  faListCheck,
  faServer,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Link } from "react-router-dom";

function Navigation() {
  return (
    <Box as="nav">
      <Stack spacing={4}>
        <HStack align="center" space={3}>
          <FontAwesomeIcon icon={faListCheck} />
          <Link ml={3} to="/tasks">
            Tasks
          </Link>
        </HStack>
        <HStack align="center">
          <FontAwesomeIcon icon={faRobot} />
          <Link ml={3} to="/agents">
            Agents
          </Link>
        </HStack>
        <HStack align="center">
          <FontAwesomeIcon icon={faServer} />
          <Link ml={3} to="#">
            Resources
          </Link>
        </HStack>
        <HStack align="center">
          <FontAwesomeIcon icon={faCog} />
          <Link ml={3} to="#">
            Settings
          </Link>
        </HStack>
        <HStack align="center" spacing={3}>
          <FontAwesomeIcon icon={faSignOutAlt} />
          <Link ml={3} to="#">
            Logout
          </Link>
        </HStack>
      </Stack>
    </Box>
  );
}

export default Navigation;
