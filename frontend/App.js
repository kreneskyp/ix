import React from "react";
import { ChakraProvider, ColorModeScript } from "@chakra-ui/react";
import { RouterProvider } from "react-router-dom";
import { RelayEnvironmentProvider } from "react-relay";
import environment from "environment";
import theme from "theme";

export const App = ({ router }) => {
  return (
    <>
      <ColorModeScript initialColorMode={theme.config.initialColorMode} />
      <RelayEnvironmentProvider environment={environment}>
        <ChakraProvider theme={theme}>
          <RouterProvider router={router} />
        </ChakraProvider>
      </RelayEnvironmentProvider>
    </>
  );
};

export default App;
