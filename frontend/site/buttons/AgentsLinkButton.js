import React from "react";
import { IconButton } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAddressBook } from "@fortawesome/free-solid-svg-icons";
import { Link } from "react-router-dom";
import { useSideBarColorMode } from "chains/editor/useColorMode";

export const AgentsLinkButton = () => {
  const style = useSideBarColorMode();
  return (
    <Link ml={3} to="/agents">
      <IconButton
        icon={<FontAwesomeIcon icon={faAddressBook} />}
        title={"Agents"}
        {...style.button}
      />
    </Link>
  );
};
