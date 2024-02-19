import React from "react";
import { Box, VStack } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";

const containerStyle = {
  minWidth: "20px",
  height: "100%",
};

const Spacer = () => {
  const lineStyle = {
    width: "2px",
    flexGrow: 1,
    backgroundColor: "transparent",
    alignSelf: "center",
  };

  return <Box sx={lineStyle} height={"100%"} m={0} p={0} />;
};

const VerticalLine = ({ flexGrow, ...props }) => {
  const lineStyle = {
    width: "2px",
    flexGrow: flexGrow !== undefined ? flexGrow : 1,
    alignSelf: "center",
  };
  const { colorMode } = useColorMode();
  const isLight = colorMode === "light";

  return (
    <Box
      sx={lineStyle}
      height={"100%"}
      m={0}
      p={0}
      bg={isLight ? "blackAlpha.400" : "gray.600"}
      {...props}
    />
  );
};

export const BranchLine = ({ height }) => {
  return (
    <Box display="flex" flexDirection="column" height={`${height}px`} ml={2}>
      <VStack
        flex={1}
        spacing={0}
        align="center"
        sx={containerStyle}
        height={"100%"}
      >
        <VerticalLine height={"33px"} />
        <Box
          height="2px"
          width="10px"
          backgroundColor="gray.500"
          ml={"10px"}
          flexGrow={0}
        />
        <VerticalLine />
      </VStack>
    </Box>
  );
};

export const TreeItem = ({ isFirst, isLast, children }) => {
  return (
    <Box display="flex" flexDirection="column" height="100%">
      <VStack
        flex={1}
        spacing={0}
        align="center"
        sx={containerStyle}
        height={"100%"}
      >
        {isFirst ? <Spacer /> : <VerticalLine />}
        <Box m={0} p={0} py={1}>
          {children}
        </Box>
        {isLast ? <Spacer /> : <VerticalLine />}
      </VStack>
    </Box>
  );
};

export default TreeItem;
