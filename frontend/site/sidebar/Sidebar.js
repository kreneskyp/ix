import React from "react";
import { Box } from "@chakra-ui/react";
import {
  useLeftSidebarContext,
  useRightSidebarContext,
} from "site/sidebar/context";
import RightSidebarSizer from "site/sidebar/RightSidebarSizer";
import { useSideBarStyle } from "site/sidebar/useSidebarStyle";
import { NO_SCROLLBAR_CSS } from "site/css";

const TRANSITION_VISIBLE = {
  opacity: 1,
  transition: "opacity 0.2s ease-out",
};

const TRANSITION_HIDDEN = {
  opacity: 0,
  transition: "opacity 0.2s ease-out",
};

/**
 *
 * Hook to delay showing content until sidebar is fully open to
 */
const useDelayContent = (value, visibleProps, hiddenProps) => {
  const [isVisible, setVisible] = React.useState(value);

  // Immediately hides content is hidden
  // Delay showing content if it is visible
  React.useEffect(() => {
    if (!value) {
      setVisible(false);
    } else {
      const timer = setTimeout(() => setVisible(true), 300);
      return () => clearTimeout(timer);
    }
  }, [value]);

  const style = isVisible
    ? visibleProps || TRANSITION_VISIBLE
    : hiddenProps || TRANSITION_HIDDEN;
  return { isVisible, style };
};

const SideBar = ({ position, children }) => {
  const leftContext = useLeftSidebarContext();
  const rightContext = useRightSidebarContext();

  const style = useSideBarStyle();
  const { sizes, isOpen, size } =
    position === "left" ? leftContext : rightContext;
  const { style: delayedContentStyle } = useDelayContent(isOpen);

  // convert list of tuples to map
  const sizeMap = {
    ...Object.fromEntries(sizes),
  };

  const sidebarStyle = {
    width: isOpen ? sizeMap[size] || sizeMap.md : 0,
    height: "100vh",
    padding: isOpen ? "0" : "0",
    position: "fixed",
    top: "0",
    overflowY: "auto",
    zIndex: 10,
    [position]: "0",

    // add left/right shadow
    boxShadow: isOpen ? "0 0 10px rgba(0,0,0,0.5)" : "none",

    // no scrollbars
    scrollbarWidth: "none",
    msOverflowStyle: "none",
    "&::WebkitScrollbar": {
      width: "0 !important",
      background: "transparent !important",
    },

    transition: "width 0.2s ease-in",
  };

  return (
    <Box style={sidebarStyle} {...style.content} css={NO_SCROLLBAR_CSS}>
      <RightSidebarSizer />
      <Box style={delayedContentStyle}>{children}</Box>
    </Box>
  );
};

export default SideBar;
