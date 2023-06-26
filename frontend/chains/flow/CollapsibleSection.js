import React, { useCallback, useState } from "react";
import { Box, Collapse, Flex } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faChevronDown,
  faChevronRight,
} from "@fortawesome/free-solid-svg-icons";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const CollapsibleSection = ({ title, children, ...props }) => {
  const [show, setShow] = useState(false);
  const toggle = useCallback(() => setShow(!show), [show]);
  const { node } = useEditorColorMode();

  return (
    <Box {...props}>
      <Flex
        px={2}
        py={1}
        fontSize="xs"
        onClick={toggle}
        cursor="pointer"
        width="100%"
        justifyContent="space-between"
        align="center"
        sx={node.header}
        bg="blackAlpha.200"
      >
        {title} <FontAwesomeIcon icon={show ? faChevronDown : faChevronRight} />
      </Flex>
      <Collapse in={show}>
        <Box p={2} fontSize="sm">
          {children}
        </Box>
      </Collapse>
    </Box>
  );
};
