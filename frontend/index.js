import React from "react";
import * as ReactDOMClient from "react-dom/client";

import { createBrowserRouter } from "react-router-dom";

import App from "./App";
import routes from "routes";
import theme from "theme";
import { ColorModeScript } from "@chakra-ui/react";

const container = document.getElementById("root");

// Create a root.
const root = ReactDOMClient.createRoot(container);

const router = createBrowserRouter(routes);

// Initial render: Render an element to the root.
root.render(
  <>
    <ColorModeScript initialColorMode={theme.config.initialColorMode} />
    <App router={router} />
  </>
);
