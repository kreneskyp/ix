import React from "react";
import { Link } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faDiagramProject } from "@fortawesome/free-solid-svg-icons";
import { MenuItem } from "site/MenuItem";

export const NewAgentButton = () => {
  return (
    <Link to="/chains">
      <MenuItem title={"Flow Editor"}>
        <FontAwesomeIcon icon={faDiagramProject} />
      </MenuItem>
    </Link>
  );
};
