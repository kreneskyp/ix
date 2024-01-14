import { useEditorColorMode } from "chains/editor/useColorMode";
import { useScrollbarCSS } from "hooks/useScrollbarCSS";

export const useSelectStyles = () => {
  const { input: styles } = useEditorColorMode();

  return {
    menuPortal: (base) => ({ ...base, zIndex: 99999 }),
    valueContainer: (base) => ({ ...base, padding: 0 }),
    input: (base) => ({ ...base, ...styles }),
    menuList: (base) => ({ ...base, ...useScrollbarCSS() }),
  };
};
