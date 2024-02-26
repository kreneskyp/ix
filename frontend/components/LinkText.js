import React from "react";
import { Text } from "@chakra-ui/react";

export const LinkText = ({ children, ...props }) => (
  <Text
    as={"span"}
    color={"blue.300"}
    css={{ textDecoration: "underline dotted" }}
    mr={1}
    cursor={"pointer"}
    {...props}
  >
    {children}
  </Text>
);
