import React from "react";

import { Box, HStack, Text } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircleXmark, faPlusCircle } from "@fortawesome/free-solid-svg-icons";
import { EditorViewState } from "chains/ChainEditorView";
import { TabState } from "chains/hooks/useTabState";

const EditorTab = ({ tab, isActive, index, setIndex, removeTab, ...props }) => {
  const { colorMode } = useColorMode();
  const ref = React.useRef();

  // grab focus when tab is active for the first time.
  React.useEffect(() => {
    if (isActive && ref.current) {
      ref.current.focus();
    }
  }, [ref, isActive]);

  const tabStyle = {
    light: {
      bg: isActive ? "gray.100" : "transparent",
      borderBottom: isActive ? "1px solid" : undefined,
      borderColor: isActive ? "blue.400" : undefined,
      _hover: {
        bg: "gray.100",
      },
    },
    dark: {
      bg: isActive ? "gray.900" : "transparent",
      borderBottom: isActive ? "1px solid" : undefined,
      borderColor: isActive ? "blue.400" : undefined,
      _hover: {
        bg: "gray.900",
      },
    },
  };

  const removeIconStyle = {
    visibility: "hidden",
    color: "whiteAlpha.300",
    _groupHover: {
      visibility: "visible",
    },
    _hover: {
      color: "gray.400",
    },
  };

  const tabGroupStyle = colorMode === "light" ? tabStyle.light : tabStyle.dark;

  return (
    <HStack
      key={index}
      px={3}
      py={1}
      mt={2}
      borderRadius={"5px 5px 0 0"}
      maxW={200}
      cursor="pointer"
      {...tabGroupStyle}
      role="group"
      onClick={() => setIndex(index)}
      tabIndex={0}
      ref={ref}
      _focus={{
        outline: "none",
        boxShadow: "none",
      }}
    >
      <Text fontSize={"xs"} mr={2}>
        {tab?.chain?.name || "unnamed"}{" "}
      </Text>
      <Text
        cursor="pointer"
        onClick={(e) => {
          removeTab(index);
          e.stopPropagation();
        }}
        {...removeIconStyle}
      >
        <FontAwesomeIcon icon={faCircleXmark} size={"xs"} />
      </Text>
    </HStack>
  );
};

export const EditorTopBar = ({ ...props }) => {
  const { colorMode } = useColorMode();
  const {
    index: activeIndex,
    setIndex,
    state: tabState,
    removeTab,
  } = React.useContext(TabState);
  const { addChain } = React.useContext(EditorViewState);

  const onAdd = React.useCallback(() => {
    addChain();
  }, [tabState]);

  const style =
    colorMode === "light"
      ? {
          bg: "gray.200",
          add: {
            color: "blackAlpha.400",
            _hover: {
              color: "blackAlpha.700",
            },
          },
        }
      : {
          bg: "blackAlpha.200",
          add: {
            color: "whiteAlpha.400",
            _hover: {
              color: "green.300",
            },
          },
        };

  return (
    <HStack width={"100%"} bg={style.bg} alignItems={"end"} pl={2}>
      <HStack>
        {tabState.map((tab, index) => (
          <EditorTab
            tab={tab}
            index={index}
            key={index}
            isActive={index === activeIndex}
            setIndex={setIndex}
            removeTab={removeTab}
          />
        ))}
      </HStack>
      <Box
        px={2}
        pb={1}
        alignItems={"center"}
        onClick={onAdd}
        {...style.add}
        cursor="pointer"
      >
        <FontAwesomeIcon icon={faPlusCircle} size={"xs"} />
      </Box>
    </HStack>
  );
};
