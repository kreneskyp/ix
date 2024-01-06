import React from "react";
import ContainerEdge from "components/flow/ContainerEdge";
import { Box } from "@chakra-ui/react";

import { InputMaskIcon } from "icons/InputMaskIcon";

export const FlowEdge = (props) => {
  return (
    <ContainerEdge {...props}>
      <Box
        width="25px"
        height="25px"
        borderRadius="50%"
        backgroundColor="gray.700"
        border="0px solid"
        borderColor="gray.600"
        display="flex"
        alignItems="center"
        justifyContent="center"
        cursor="pointer"
      >
        <InputMaskIcon color="white" />
      </Box>
    </ContainerEdge>
  );
};
