import React from "react";
import { Link } from "react-router-dom";
import { IconButton } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faDiagramProject } from "@fortawesome/free-solid-svg-icons";

export const NewAgentButton = () => {
  const { colorMode } = useColorMode();

  return (
    <Link to="/chains/new">
      <IconButton
        width="100%"
        border="1px solid"
        borderColor={colorMode === "light" ? "gray.300" : "whiteAlpha.50"}
        icon={<FontAwesomeIcon icon={faDiagramProject} />}
        title={"New Agent or Chain"}
      >
        New Agent
      </IconButton>
    </Link>
  );
};
