import React from "react";
import { Box, Spinner } from "@chakra-ui/react";

export const CenteredSpinner = (props) => {
  return (
    <Box
      height="100vh"
      display="flex"
      alignItems="center"
      justifyContent="center"
    >
      <Spinner size="xl" {...props} />
    </Box>
  );
};

export default CenteredSpinner;
