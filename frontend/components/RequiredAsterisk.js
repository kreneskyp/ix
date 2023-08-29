import React from "react";
import { Text } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";

export const RequiredAsterisk = ({ color }) => {
  const { colorMode } = useColorMode();
  const _color = color || (colorMode === "light" ? "red.500" : "red.300");
  return (
    <Text as="span" color={_color}>
      *
    </Text>
  );
};
