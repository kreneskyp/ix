import React from "react";
import { Link } from "react-router-dom";
import { Button, Icon, IconButton } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus, faUserPlus } from "@fortawesome/free-solid-svg-icons";

export const NewAgentButton = () => {
  const { colorMode } = useColorMode();

  return (
    <Link to="/chains/new">
      <IconButton
        width="100%"
        border="1px solid"
        borderColor={colorMode === "light" ? "gray.300" : "whiteAlpha.50"}
        icon={<FontAwesomeIcon icon={faUserPlus} />}
        title={"New Agent"}
      >
        New Agent
      </IconButton>
    </Link>
  );
};
