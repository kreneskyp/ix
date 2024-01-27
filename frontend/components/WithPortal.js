import React from "react";
import ReactDOM from "react-dom";

/**
 * Renders children in a portal. If root is not provided, defaults to document.body.
 * Useful for breaking a component out of the normal layering of the DOM.
 */
export const WithPortal = ({ children, root }) => {
  return ReactDOM.createPortal(children, root || document.body);
};
