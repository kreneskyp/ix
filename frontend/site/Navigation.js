import React from "react";
import { Box, HStack, Stack } from "@chakra-ui/react";
import {
  faCog,
  faSignOutAlt,
  faRobot,
  faListCheck,
  faServer,
  faChain,
  faMessage,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Link } from "react-router-dom";
import { useColorMode } from "@chakra-ui/color-mode";

function Navigation() {
  const { colorMode } = useColorMode();

  return (
    <Box
      as="nav"
      fontSize="sm"
      color={colorMode === "light" ? "gray.900" : "gray.200"}
    >
      <Stack spacing={3}>
        <HStack align="center">
          <FontAwesomeIcon icon={faMessage} />
          <Link ml={3} to="/chats">
            Chats
          </Link>
        </HStack>

        <HStack align="center">
          <FontAwesomeIcon icon={faChain} />
          <Link ml={3} to="/chains">
            Chains
          </Link>
        </HStack>
        <HStack align="center">
          <FontAwesomeIcon icon={faRobot} />
          <Link ml={3} to="/agents">
            Agents
          </Link>
        </HStack>
        {false && (
          <HStack align="center">
            <FontAwesomeIcon icon={faServer} />
            <Link ml={3} to="#">
              Resources
            </Link>
          </HStack>
        )}
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
