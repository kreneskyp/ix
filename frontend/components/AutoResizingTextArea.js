import React, { useEffect, useRef } from "react";
import { Textarea } from "@chakra-ui/react";

export const AutoResizingTextarea = ({ ...props }) => {
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, []); // Empty dependency array to run only once after the initial render

  return <Textarea ref={textareaRef} {...props} />;
};

export default AutoResizingTextarea;
