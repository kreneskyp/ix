import React from "react";
import PropTypes from "prop-types";
import { Box, Text } from "@chakra-ui/react";
import { Global } from "@emotion/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser, faRobot, faCog } from "@fortawesome/free-solid-svg-icons";
import { spin } from "site/key_frames";
import { useChatStyle } from "chat/ChatInterface";

const ChatMessageAvatar = ({ message, isThinking }) => {
  if (!message) {
    return null;
  }

  const avatarSize = "40px";
  const iconSize = "lg";

  const { avatar } = useChatStyle();
  const { bg, color, border, borderColor, avatarColor } = avatar;

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
      border={border}
      borderRadius="full"
      borderColor={borderColor}
      bg={bg}
      color={color}
      width={avatarSize}
      height={avatarSize}
      position="relative"
      _before={{
        content: '""',
        position: "absolute",
        width: "calc(100% + 4px)",
        height: "calc(100% + 4px)",
        border: border,
        borderRadius: "50%",
        boxSizing: "border-box",
        borderColor: isThinking
          ? "#63B3ED transparent #63B3ED transparent"
          : borderColor,
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
          : "transparent",
        animation: isThinking ? "spin 1.2s linear infinite" : "none",
        zIndex: "1",
        filter: isThinking ? "blur(4px)" : "none",
      }}
    >
      <Global styles={spin} />
      <Text color={avatarColor}>
        {getAvatarByRole(message.content.agent ? "ASSISTANT" : message.role)}
      </Text>
    </Box>
  );
};

ChatMessageAvatar.propTypes = {
  message: PropTypes.shape({
    role: PropTypes.oneOf(["USER", "ASSISTANT", "SYSTEM"]).isRequired,
    created_at: PropTypes.string.isRequired,
  }).isRequired,
};

ChatMessageAvatar.defaultProps = {
  isThinking: false,
};

export default ChatMessageAvatar;
