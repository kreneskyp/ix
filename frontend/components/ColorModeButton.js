import React from "react";
import { useColorMode } from "@chakra-ui/color-mode";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faMoon, faSun } from "@fortawesome/free-solid-svg-icons";
import { MenuItem } from "site/MenuItem";

export const ColorModeButton = () => {
  const { colorMode, toggleColorMode } = useColorMode();

  const icon = colorMode === "light" ? faMoon : faSun;
  const title = colorMode === "light" ? "Dark Mode" : "Light Mode";
  return (
    <MenuItem title={title} onClick={toggleColorMode}>
      <FontAwesomeIcon icon={icon} />
    </MenuItem>
  );
};
