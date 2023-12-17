import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faMessage, faClock } from "@fortawesome/free-solid-svg-icons";
import { useColorMode } from "@chakra-ui/color-mode";
import { Box } from "@chakra-ui/layout";
import { StackableIcon } from "icons/StackableIcon";
import { IndicatorIcon } from "icons/IndicatorIcon";

const ChatHistoryIcon = () => {
  const { colorMode } = useColorMode();
  const iconColor = colorMode === "light" ? "gray.200" : "black";

  return (
    <StackableIcon>
      <FontAwesomeIcon icon={faMessage} size={"sm"} />
      <IndicatorIcon indicatorSize={11}>
        <FontAwesomeIcon icon={faClock} />
      </IndicatorIcon>
    </StackableIcon>
  );
};

export default ChatHistoryIcon;
