import React from "react";
import { Link } from "react-router-dom";
import { Button, Icon } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus } from "@fortawesome/free-solid-svg-icons";

export const NewAgentButton = () => {
  const { colorMode } = useColorMode();

  return (
    <Link to="/agents/new">
      <Button
        width="100%"
        border="1px solid"
        borderColor={colorMode === "light" ? "gray.300" : "whiteAlpha.50"}
        leftIcon={<Icon as={FontAwesomeIcon} icon={faPlus} />}
      >
        New Agent
      </Button>
    </Link>
  );
};
