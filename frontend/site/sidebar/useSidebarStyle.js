import { useColorMode } from "@chakra-ui/color-mode";

export const useSideBarStyle = () => {
  const { colorMode } = useColorMode();
  const dark = {
    header: {
      color: "gray.500",
    },
    headerContainer: {
      borderBottom: "1px solid",
      borderColor: "blackAlpha.100",
      bg: "blackAlpha.400",
    },
    content: {
      bg: "gray.700",
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
    content: {
      bg: "white",
    },
    icon: {
      color: "gray.400",
    },
  };
  return colorMode === "dark" ? dark : light;
};
