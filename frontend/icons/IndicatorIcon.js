import React from "react";
import { Box } from "@chakra-ui/react";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const IndicatorIcon = ({ children, color, indicatorSize }) => {
  const { isLight, indicator } = useEditorColorMode();
  const bg = isLight ? "gray.100" : "gray.800";

  const indicatorStyle = {
    position: "absolute",
    bottom: 0,
    right: 0,
    transform: "translate(40%, 0%)",
    width: indicatorSize + 2 + "px", // Adjust size as needed
    height: indicatorSize + 2 + "px", // Adjust size as needed
    borderRadius: "50%",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  };

  const iconStyle = {
    fontSize: indicatorSize + "px",
  };

  return (
    <Box bg={bg} style={indicatorStyle} color={color} fontSize={"24px"}>
      {children ? React.cloneElement(children, { style: iconStyle }) : null}
    </Box>
  );
};
