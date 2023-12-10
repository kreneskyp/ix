import React from "react";
import { Box, Divider, HStack, IconButton, Stack } from "@chakra-ui/react";
import { faServer, faMessage } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Link } from "react-router-dom";
import { useColorMode } from "@chakra-ui/color-mode";
import { SecretsMenuItem } from "secrets/SecretsMenuItem";
import { MenuItem } from "site/MenuItem";

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
        <Link ml={3} to="/chats">
          <MenuItem title="Chat History">
            <FontAwesomeIcon icon={faMessage} />
          </MenuItem>
        </Link>
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
        <MenuItem>
          <SecretsMenuItem />
        </MenuItem>
        <Divider
          borderColor={colorMode === "light" ? "gray.400" : "whiteAlpha.400"}
        />
      </Stack>
    </Box>
  );
}

export default Navigation;
