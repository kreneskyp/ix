import React from "react";
import { useColorMode } from "@chakra-ui/color-mode";
import { Button, IconButton } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faMoon } from "@fortawesome/free-solid-svg-icons";
import { faSun } from "@fortawesome/free-regular-svg-icons";

export const ColorModeButton = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const style =
    colorMode === "light"
      ? {
          text: "Dark Mode",
          border: "1px solid",
          borderColor: "gray.300",
        }
      : {
          title: "Light Mode",
          border: "1px solid",
          borderColor: "whiteAlpha.50",
        };

  const icon = colorMode === "light" ? faMoon : faSun;
  const title = colorMode === "light" ? "Dark Mode" : "Light Mode";
  return (
    <header>
      <IconButton
        {...style}
        icon={<FontAwesomeIcon icon={icon} />}
        onClick={toggleColorMode}
      >
        Toggle {colorMode === "light" ? "Dark" : "Light"}
      </IconButton>
    </header>
  );
};
