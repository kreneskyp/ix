import React from "react";
import { Link } from "react-router-dom";
import { Button } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPencil } from "@fortawesome/free-solid-svg-icons";

export const AgentEditButton = ({ agent, ...props }) => {
  return (
    <Link to={`/chains/${agent.chain_id}`}>
      <Button size={"sm"} {...props}>
        <FontAwesomeIcon icon={faPencil} style={{ marginRight: "5px" }} /> Edit
      </Button>
    </Link>
  );
};
