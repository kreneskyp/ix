import { useTheme } from "@chakra-ui/react";

export const useScrollbarCSS = () => {
  const theme = useTheme();
  return {
    "&::-webkit-scrollbar": {
      width: "5px",
      padding: "2px",
    },
    "&::-webkit-scrollbar-track": {
      background: "transparent",
    },
    "&::-webkit-scrollbar-thumb": {
      background: theme.colors.gray[300],
      borderRadius: "2px",
    },
    "&::-webkit-scrollbar-thumb:hover": {
      background: theme.colors.gray[300],
    },
  };
};
