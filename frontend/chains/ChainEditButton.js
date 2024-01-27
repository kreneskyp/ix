import React from "react";
import { Link } from "react-router-dom";
import { Button } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPencil } from "@fortawesome/free-solid-svg-icons";
import { EditorViewState } from "chains/editor/contexts";

export const ChainEditButton = ({ chain, ...props }) => {
  const editor = React.useContext(EditorViewState);

  if (editor === null) {
    return (
      <Link to={`/chains/${chain.id}`}>
        <Button size={"sm"} {...props}>
          <FontAwesomeIcon icon={faPencil} style={{ marginRight: "5px" }} />{" "}
          Edit
        </Button>
      </Link>
    );
  } else {
    const onClick = () => {
      editor.selectOrOpenChain(chain.id);
    };

    return (
      <Button size={"sm"} {...props} onClick={onClick}>
        <FontAwesomeIcon icon={faPencil} style={{ marginRight: "5px" }} /> Edit
      </Button>
    );
  }
};
