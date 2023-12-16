import React, { createContext, useState, useContext } from "react";

const SidebarContext = createContext(null);

export const DEFAULT_SIZES_LEFT = [
  ["icons", "32px"],
  ["text", "175px"],
];

export const DEFAULT_SIZES_RIGHT = [
  ["2xl", "850px"],
  ["xl", "650px"],
  ["lg", "450px"],
  ["md", "350px"],
  ["sm", "250px"],
];

export const DEFAULT_SIZES_RIGHT_ORDER = ["sm", "md", "lg", "xl"];

// Hook for accessing the entire sidebar context
export const useSidebarContext = () => useContext(SidebarContext);

// Hook for accessing the left sidebar's context
export const useLeftSidebarContext = () => {
  const context = useContext(SidebarContext);
  if (!context) {
    throw new Error(
      "useLeftSidebarContext must be used within a SidebarProvider"
    );
  }
  return context.left;
};

// Hook for accessing the right sidebar's context
export const useRightSidebarContext = () => {
  const context = useContext(SidebarContext);
  if (!context) {
    throw new Error(
      "useRightSidebarContext must be used within a SidebarProvider"
    );
  }
  return context.right;
};

export const SidebarProvider = ({ sizes_left, sizes_right, children }) => {
  // State for the left sidebar
  const [isLeftOpen, setLeftIsOpen] = useState(true);
  const [leftSize, setLeftSize] = useState("icons");
  const toggleLeftSidebar = () => setLeftIsOpen(!isLeftOpen);

  // State for the right sidebar
  const [isRightOpen, setRightIsOpen] = useState(true);
  const [rightSize, setRightSize] = useState("md");
  const toggleRightSidebar = () => setRightIsOpen(!isRightOpen);

  const leftWidth = isLeftOpen
    ? sizes_left.find((s) => s[0] === leftSize)[1]
    : "0px";
  const rightWidth = isRightOpen
    ? sizes_right.find((s) => s[0] === rightSize)[1]
    : "0px";

  return (
    <SidebarContext.Provider
      value={{
        left: {
          sizes: sizes_left,
          isOpen: isLeftOpen,
          size: leftSize,
          setSize: setLeftSize,
          width: leftWidth,
          toggleSidebar: toggleLeftSidebar,
        },
        right: {
          sizes: sizes_right,
          isOpen: isRightOpen,
          size: rightSize,
          setSize: setRightSize,
          width: rightWidth,
          toggleSidebar: toggleRightSidebar,
        },
      }}
    >
      {children}
    </SidebarContext.Provider>
  );
};

SidebarProvider.defaultProps = {
  sizes_left: DEFAULT_SIZES_LEFT,
  sizes_right: DEFAULT_SIZES_RIGHT,
};

export default SidebarProvider;
