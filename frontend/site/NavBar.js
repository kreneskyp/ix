import React from "react";
import {
  Box,
  Flex,
  Spacer,
  HStack,
  VStack,
  Avatar,
  IconButton,
} from "@chakra-ui/react";
import { Link } from "react-router-dom";
import { CheckIcon } from "@chakra-ui/icons";

const Navbar = () => {
  return (
    <Box bg="blue.500" color="white" p={4}>
      <Flex align="center">
        <Box>
          <Link to="/">
            <h2>My App Name</h2>
          </Link>
        </Box>
        <Spacer />
        <HStack spacing={8}>
          <Link to="/tasks">
            <h4>Tasks</h4>
          </Link>
          <Link to="/agents">
            <h4>Agents</h4>
          </Link>
          <Link to="/tasks/chat">
            <h4>Chat</h4>
          </Link>
          <Spacer />
          <VStack spacing={1}>
            <Link to="/users/settings">
              <Avatar name="User Name" src="https://bit.ly/broken-link" />
            </Link>
            <h6>User Name</h6>
          </VStack>
          <IconButton
            icon={<CheckIcon />}
            aria-label="Admin Settings"
            variant="ghost"
            fontSize="20px"
            onClick={() => {
              window.location.href = "/admin/settings";
            }}
          />
        </HStack>
      </Flex>
    </Box>
  );
};

export default Navbar;
