import React from "react";
import { Box, Divider, HStack, IconButton, Stack } from "@chakra-ui/react";
import {
  faCog,
  faSignOutAlt,
  faServer,
  faMessage,
  faAddressBook,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Link } from "react-router-dom";
import { useColorMode } from "@chakra-ui/color-mode";

function Navigation() {
  const { colorMode } = useColorMode();
  const style =
    colorMode === "light"
      ? {
          border: "1px solid",
          borderColor: "gray.300",
        }
      : {
          border: "1px solid",
          borderColor: "whiteAlpha.50",
        };

  return (
    <Box as="nav" color={colorMode === "light" ? "gray.900" : "gray.200"}>
      <Stack spacing={3}>
        <HStack align="center">
          <Link ml={3} to="/chats">
            <IconButton
              icon={<FontAwesomeIcon icon={faMessage} />}
              title={"Chat history"}
              {...style}
            />
          </Link>
        </HStack>
        <HStack align="center">
          <Link ml={3} to="/agents">
            <IconButton
              icon={<FontAwesomeIcon icon={faAddressBook} />}
              title={"Agents"}
              {...style}
            />
          </Link>
        </HStack>
        {false && (
          <HStack align="center">
            <Link ml={3} to="#">
              <IconButton
                icon={<FontAwesomeIcon icon={faServer} />}
                title={"Resources"}
                {...style}
              />
            </Link>
          </HStack>
        )}
        <Divider
          borderColor={colorMode === "light" ? "gray.400" : "whiteAlpha.400"}
        />
        <HStack align="center">
          <Link ml={3} to="#">
            <IconButton
              icon={<FontAwesomeIcon icon={faCog} />}
              title={"Settings"}
              {...style}
            />
          </Link>
        </HStack>
        <HStack align="center" spacing={3}>
          <Link ml={3} to="#">
            <IconButton
              icon={<FontAwesomeIcon icon={faSignOutAlt} />}
              title={"Sign out"}
              {...style}
            />
          </Link>
        </HStack>
      </Stack>
    </Box>
  );
}

export default Navigation;
