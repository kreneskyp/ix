import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faMessage, faPlus } from "@fortawesome/free-solid-svg-icons";
import { useColorMode } from "@chakra-ui/color-mode";

const PlusMessageIcon = () => {
  const { colorMode } = useColorMode();
  const iconColor = colorMode === "light" ? "black" : "black";
  return (
    <span className="fa-stack">
      <FontAwesomeIcon icon={faMessage} className="fa-stack-1x" />
      <FontAwesomeIcon
        icon={faPlus}
        size={"xs"}
        className="fa-stack-1x"
        fontWeight={"bold"}
        color={iconColor}
        style={{ position: "absolute", top: -1.5 }}
      />
    </span>
  );
};
export default PlusMessageIcon;
