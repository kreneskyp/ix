import React from "react";
import { Box, HStack, IconButton } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRightLeft, faCircle } from "@fortawesome/free-solid-svg-icons";
import { useRightSidebarContext } from "site/sidebar/context";
import { useSideBarStyle } from "site/sidebar/useSidebarStyle";

const SidebarSizer = () => {
  const { sizes, isOpen, size, setSize, toggleSidebar } =
    useRightSidebarContext();
  const style = useSideBarStyle();

  const sizeMap = {
    ...Object.fromEntries(sizes),
  };

  return (
    <HStack {...style.headerContainer}>
      <IconButton
        aria-label="hide"
        bg={"transparent"}
        icon={<FontAwesomeIcon icon={faRightLeft} />}
        size={"xs"}
        title={"Toggle sidebar"}
        onClick={toggleSidebar}
        {...style.header}
      />
      />
      {sizes?.map(([key, _], i) => (
        <Box
          key={i}
          as={"span"}
          color={size === key ? "green.400" : "gray"}
          fontSize={8}
        >
          <FontAwesomeIcon
            icon={faCircle}
            onClick={() => setSize(key)}
            style={{ cursor: "pointer" }}
          />
        </Box>
      ))}
    </HStack>
  );
};

export default SidebarSizer;
