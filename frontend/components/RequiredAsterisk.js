import React from "react";
import { Text } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";

export const RequiredAsterisk = () => {
  const { colorMode } = useColorMode();
  const color = colorMode === "light" ? "red.500" : "red.200";
  return (
    <Text as="span" color={color}>
      *
    </Text>
  );
};
