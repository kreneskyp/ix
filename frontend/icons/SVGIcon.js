import React from "react";
import { Box, useToken } from "@chakra-ui/react";

export const SVGIcon = ({ color, bg, children, svgProps, ...props }) => {
  const colorToken = useToken("colors", color || "white");

  return (
    <Box display={"flex"} alignItems={"center"} m={0} p={0} {...props}>
      <svg
        width="1.2em"
        height="1.2em"
        viewBox="0 0 128 128"
        fill={colorToken}
        {...(svgProps || {})}
      >
        {children}
      </svg>
    </Box>
  );
};

export default SVGIcon;
