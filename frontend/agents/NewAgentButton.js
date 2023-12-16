import React from "react";
import { Link } from "react-router-dom";
import { Tooltip } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faDiagramProject } from "@fortawesome/free-solid-svg-icons";
import { MenuItem } from "site/MenuItem";

export const NewAgentButton = () => {
  return (
    <Tooltip label="New Agent" aria-label="New Agent">
      <Link to="/chains/new">
        <MenuItem title={"New Agent"}>
          <FontAwesomeIcon icon={faDiagramProject} />
        </MenuItem>
      </Link>
    </Tooltip>
  );
};
