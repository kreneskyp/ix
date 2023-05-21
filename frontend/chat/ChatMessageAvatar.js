import React from "react";
import PropTypes from "prop-types";
import { Box, useColorModeValue } from "@chakra-ui/react";
import { Global } from "@emotion/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser, faRobot, faCog } from "@fortawesome/free-solid-svg-icons";
import { spin } from "site/key_frames";

const ChatMessageAvatar = ({ message, isThinking }) => {
  if (!message) {
    return null;
  }

  const avatarSize = "40px";
  const iconSize = "lg";
  const bgColor = useColorModeValue("gray.200", "gray.700");
  const color = useColorModeValue("black", "gray.500");
  const border = useColorModeValue("gray.300", "transparent");

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
    <Box
      display="flex"
      alignItems="center"
      justifyContent="center"
      border="2px solid"
      borderRadius="full"
      borderColor={border}
      bg={bgColor}
      color={color}
      width={avatarSize}
      height={avatarSize}
      position="relative"
      _before={{
        content: '""',
        position: "absolute",
        width: "calc(100% + 4px)",
        height: "calc(100% + 4px)",
        border: "2px solid",
        borderRadius: "50%",
        boxSizing: "border-box",
        borderColor: isThinking
          ? "#63B3ED transparent #63B3ED transparent"
          : border,
        animation: isThinking ? "spin 1.2s linear infinite" : "none",
        zIndex: "1",
      }}
      _after={{
        content: '""',
        position: "absolute",
        width: "calc(100% + 8px)",
        height: "calc(100% + 8px)",
        border: "2px solid",
        borderRadius: "50%",
        boxSizing: "border-box",
        borderColor: isThinking
          ? "#63B3ED transparent #63B3ED transparent"
          : border,
        animation: isThinking ? "spin 1.2s linear infinite" : "none",
        zIndex: "1",
        filter: isThinking ? "blur(4px)" : "none",
      }}
    >
      <Global styles={spin} />
      {getAvatarByRole(message.content.agent ? "ASSISTANT" : message.role)}
    </Box>
  );
};

ChatMessageAvatar.propTypes = {
  message: PropTypes.shape({
    role: PropTypes.oneOf(["USER", "ASSISTANT", "SYSTEM"]).isRequired,
    createdAt: PropTypes.string.isRequired,
  }).isRequired,
};

ChatMessageAvatar.defaultProps = {
  isThinking: false,
};

export default ChatMessageAvatar;
