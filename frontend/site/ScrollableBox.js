import { Box, Grid, VStack } from "@chakra-ui/react";
import React from "react";

export const ScrollableBox = ({ children }) => {
  return (
    <Box flexGrow="1" overflowY="auto">
      <Grid h="100%" templateRows="1fr auto" alignItems="end" gap={4}>
        <VStack spacing={4} ml={4} mr={4}>
          {children}
        </VStack>
      </Grid>
    </Box>
  );
};
