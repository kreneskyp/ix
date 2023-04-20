import { Button, Icon } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { Link } from "react-router-dom";
import React from "react";

export const NewAgentButton = () => {
  return (
    <Link to="/agents/new">
      <Button
        bg="transparent"
        width="100%"
        borderStyle="dashed"
        borderWidth="2px"
        borderColor="whiteAlpha.600"
        color="whiteAlpha.800"
        leftIcon={<Icon as={FontAwesomeIcon} icon={faPlus} />}
      >
        New Agent
      </Button>
    </Link>
  );
};
