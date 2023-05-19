import React from "react";
import PropTypes from "prop-types";
import { Box, Tooltip, useColorModeValue } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser, faRobot, faCog } from "@fortawesome/free-solid-svg-icons";
import AssistantAvatar from "chat/AssistantAvatar";
import { useColorMode } from "@chakra-ui/color-mode";

const ChatMessageAvatar = ({ message }) => {
  const { colorMode } = useColorMode();

  if (!message) {
    return null;
  }

  const avatarSize = "40px";
  const iconSize = "lg";
  const bgColor = useColorModeValue("gray.200", "gray.700");
  const color = useColorModeValue("black", "gray.500");
  const getAvatarByRole = (role) => {
    switch (role) {
      case "USER":
        return <FontAwesomeIcon icon={faUser} size={iconSize} />;
      case "ASSISTANT":
        return <FontAwesomeIcon icon={faRobot} size={iconSize} />;
      case "SYSTEM":
        return <FontAwesomeIcon icon={faCog} size={iconSize} />;
      default:
        return null;
    }
  };

  return (
    <Tooltip label={message.timestamp} aria-label="Timestamp">
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        border="1px solid"
        borderRadius="full"
        borderColor={colorMode === "light" ? "gray.300" : "transparent"}
        bg={bgColor}
        color={color}
        width={avatarSize}
        height={avatarSize}
      >
        {getAvatarByRole(message.content.agent ? "ASSISTANT" : message.role)}
      </Box>
    </Tooltip>
  );
};

ChatMessageAvatar.propTypes = {
  message: PropTypes.shape({
    role: PropTypes.oneOf(["USER", "ASSISTANT", "SYSTEM"]).isRequired,
    createdAt: PropTypes.string.isRequired,
  }).isRequired,
};

export default ChatMessageAvatar;
