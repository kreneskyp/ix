import React from "react";
import { useColorMode } from "@chakra-ui/color-mode";
import { Button } from "@chakra-ui/react";

export const ColorModeButton = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  return (
    <header>
      <Button onClick={toggleColorMode}>
        Toggle {colorMode === "light" ? "Dark" : "Light"}
      </Button>
    </header>
  );
};
