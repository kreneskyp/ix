import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faMessage, faPlus } from "@fortawesome/free-solid-svg-icons";
import { useColorMode } from "@chakra-ui/color-mode";
import { Box } from "@chakra-ui/layout";
import { StackableIcon } from "icons/StackableIcon";

const PlusMessageIcon = () => {
  const { colorMode } = useColorMode();
  const iconColor = colorMode === "light" ? "gray.200" : "black";

  return (
    <StackableIcon>
      <FontAwesomeIcon icon={faMessage} />
      <Box
        style={{
          position: "absolute",
          top: "1px",
          right: "-1px",
          transform: "translate(-50%, 0%)",
        }}
        color={iconColor}
        fontSize={"xs"}
        fontWeight={"bold"}
      >
        <FontAwesomeIcon icon={faPlus} />
      </Box>
    </StackableIcon>
  );
};

export default PlusMessageIcon;
