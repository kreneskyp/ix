import React from "react";
import { Link } from "react-router-dom";
import { Tooltip } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faDiagramProject } from "@fortawesome/free-solid-svg-icons";
import { MenuItem } from "site/MenuItem";

export const NewAgentButton = () => {
  return (
    <Tooltip label="Flow Editor" aria-label="Flow Editor">
      <Link to="/chains">
        <MenuItem title={"Flow Editor"}>
          <FontAwesomeIcon icon={faDiagramProject} />
        </MenuItem>
      </Link>
    </Tooltip>
  );
};
