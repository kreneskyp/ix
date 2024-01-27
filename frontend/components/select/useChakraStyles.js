import { useColorModeValue } from "@chakra-ui/react";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { useRightSidebarContext } from "site/sidebar/context";

export const useChakraStyles = () => {
  const { input: inputStyles, isLight } = useEditorColorMode();
  const sidebar = useRightSidebarContext();
  const menuBgColor = useColorModeValue("white", "gray.800");

  return {
    control: (base) => ({
      ...base,
      ...inputStyles,
      width: `${sidebar.width}px`,
      backgroundColor: menuBgColor,
    }),
    dropdownIndicator: (base) => ({
      ...base,
      ...inputStyles,
    }),
  };
};
