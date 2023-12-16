import React from "react";
import { useSelected, useFocused } from "slate-react";
import { Text, useColorModeValue } from "@chakra-ui/react";
import { useChatColorMode } from "chains/editor/useColorMode";

export const MentionElement = ({ attributes, children, element }) => {
  const selected = useSelected();
  const focused = useFocused();

  const { mention } = useChatColorMode();
  const bg =
    selected && focused
      ? useColorModeValue("gray.200", "gray.700")
      : "transparent";

  return (
    <Text
      as="span"
      {...attributes}
      borderRadius={3}
      contentEditable={false}
      bg={bg}
      sx={mention}
    >
      @{element.display}
      {children}
    </Text>
  );
};
