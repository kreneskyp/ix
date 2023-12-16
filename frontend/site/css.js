export const SCROLLBAR_CSS = {
  scrollbarWidth: "thin", // For Firefox
  scrollbarColor: "#333 transparent", // For Firefox
  "&::-webkit-scrollbar": {
    width: "10px",
  },
  "&::-webkit-scrollbar-track": {
    background: "transparent",
  },
  "&::-webkit-scrollbar-thumb": {
    background: "#333",
    borderRadius: "4px",
  },
  "&::-webkit-scrollbar-thumb:hover": {
    background: "#555",
  },
};

export const NO_SCROLLBAR_CSS = {
  "&::-webkit-scrollbar": {
    width: "0px",
    background: "transparent",
  },
  "&::-webkit-scrollbar-track": {
    background: "transparent",
    width: "0px",
  },
  "&::-webkit-scrollbar-thumb": {
    background: "transparent",
  },
  "&::-webkit-scrollbar-thumb:hover": {
    width: "0px",
    background: "transparent",
  },
};
