import { useColorMode } from "@chakra-ui/color-mode";

export const useEditorColorMode = () => {
  const { colorMode } = useColorMode();
  const isLight = colorMode === "light";

  return {
    isLight,
    highlightColor: isLight ? "gray.100" : "gray.100",
    color: isLight ? "gray.800" : "gray.100",
    bg: isLight ? "gray.50" : "gray.700",
    border: isLight ? "gray.600" : "black",
    highlight: {
      llm: isLight ? "red.300" : "red.300",
      prompt: isLight ? "orange.300" : "orange.500",
      memory: isLight ? "purple.500" : "purple.300",
      chain: isLight ? "blue.500" : "blue.300",
      agent: isLight ? "green.500" : "green.300",
      tool: isLight ? "yellow.500" : "yellow.300",
    },
  };
};

export const useSideBarColorMode = () => {
  const { colorMode } = useColorMode();
  const isLight = colorMode === "light";

  return {
    isLight,
    highlightColor: isLight ? "gray.100" : "gray.100",
    color: isLight ? "gray.800" : "gray.100",
    bg: isLight ? "gray.300" : "gray.700",
    border: isLight ? "gray.600" : "black",
  };
};

export const useChatColorMode = () => {
  const { colorMode } = useColorMode();
  const isLight = colorMode === "light";

  return {
    isLight,
    mention: isLight ? "blue.300" : "blue.400",
    artifact: isLight ? "yellow.300" : "yellow.300",
  };
};
