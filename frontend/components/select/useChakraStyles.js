import { useEditorColorMode } from "chains/editor/useColorMode";
import { useRightSidebarContext } from "site/sidebar/context";

export const useChakraStyles = () => {
  const { input: styles } = useEditorColorMode();
  const sidebar = useRightSidebarContext();

  return {
    control: (base) => ({ ...base, ...styles, width: `${sidebar.width}px` }),
    dropdownIndicator: (base) => ({ ...base, ...styles }),
  };
};
