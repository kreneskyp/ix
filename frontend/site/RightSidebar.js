import React, { useRef } from "react";
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerOverlay,
  HStack,
  IconButton,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRightLeft, faX } from "@fortawesome/free-solid-svg-icons";
import { useColorMode } from "@chakra-ui/color-mode";

const DRAW_SIZES = ["xs", "sm", "xl"];

export const RightSidebar = ({
  isOpen,
  onOpen,
  onClose,
  children,
  sizes,
  onWheel,
  drawerRef,
  pointerEvents,
}) => {
  const btnRef = useRef();

  // drawer size state - toggle rotates through allowed sizes
  const [size, setSize] = React.useState(sizes[0]);
  const toggleSize = React.useCallback(() => {
    setSize((prev) => sizes[(sizes.indexOf(prev) + 1) % sizes.length]);
  }, [sizes]);

  // style
  const dark = {
    header: {
      color: "gray.500",
    },
    headerContainer: {
      borderBottom: "1px solid",
      borderColor: "blackAlpha.100",
      bg: "blackAlpha.400",
    },
    icon: {
      color: "gray.500",
    },
  };
  const light = {
    header: {
      color: "gray.500",
    },
    headerContainer: {
      borderBottom: "1px solid",
      borderColor: "blackAlpha.200",
      bg: "blackAlpha.50",
    },
    icon: {
      color: "gray.400",
    },
  };
  const style = useColorMode().colorMode === "dark" ? dark : light;

  return (
    <Drawer
      isOpen={isOpen}
      placement="right"
      onClose={onClose}
      finalFocusRef={btnRef}
      closeOnOverlayClick={false}
      trapFocus={false}
      size={size}
    >
      <DrawerOverlay
        style={{ backgroundColor: "transparent", pointerEvents }}
        onWheel={onWheel}
      >
        <DrawerContent
          style={{ pointerEvents: "all" }}
          height="100vh"
          display="flex"
          flexDirection="column"
          ref={drawerRef}
        >
          <DrawerHeader h={10} px={2} py={1} {...style.headerContainer}>
            <HStack display={"flex"} justifyContent={"flex-start"}>
              <IconButton
                aria-label="Expand"
                bg={"transparent"}
                icon={<FontAwesomeIcon icon={faRightLeft} />}
                size={"xs"}
                title={"Toggle width"}
                onClick={toggleSize}
                {...style.header}
              />
              <IconButton
                aria-label={"Close"}
                bg={"transparent"}
                icon={<FontAwesomeIcon icon={faX} />}
                size={"xs"}
                title={"Close"}
                onClick={onClose}
                {...style.header}
              />
            </HStack>
          </DrawerHeader>
          {children}
        </DrawerContent>
      </DrawerOverlay>
    </Drawer>
  );
};

RightSidebar.defaultProps = {
  sizes: DRAW_SIZES,
  pointerEvents: "none",
};
