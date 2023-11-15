import React from "react";
import { useSelected, useFocused } from "slate-react";
import { Text } from "@chakra-ui/react";
import { useChatColorMode } from "chains/editor/useColorMode";

export const ArtifactElement = ({ attributes, children, element }) => {
  const selected = useSelected();
  const focused = useFocused();
  const { artifact, editorHighlight } = useChatColorMode();
  const bg = selected && focused ? editorHighlight : "transparent";

  return (
    <Text
      as="span"
      {...attributes}
      borderRadius={3}
      contentEditable={false}
      bg={bg}
      sx={artifact}
    >
      &#123; {element.display} &#125;
      {children}
    </Text>
  );
};
