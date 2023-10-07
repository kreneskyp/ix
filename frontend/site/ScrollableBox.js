import { Box, Grid, VStack } from "@chakra-ui/react";
import React from "react";
import { SCROLLBAR_CSS } from "site/css";

export const ScrollableBox = React.forwardRef(({ children, ...props }, ref) => {
  return (
    <Box flexGrow="1" overflowY="auto" css={SCROLLBAR_CSS} {...props} ref={ref}>
      <Grid h="100%" templateRows="1fr auto" alignItems="end" gap={4}>
        <VStack spacing={4} ml={4} mr={4}>
          {children}
        </VStack>
      </Grid>
    </Box>
  );
});
