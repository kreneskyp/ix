import React, { useContext, useCallback } from "react";
import {
  Badge,
  Box,
  Popover,
  PopoverArrow,
  PopoverBody,
  PopoverCloseButton,
  PopoverContent,
  PopoverHeader,
  PopoverTrigger,
  Text,
  useDisclosure,
} from "@chakra-ui/react";
import { SelectedNodeContext } from "chains/editor/contexts";
import { useEditorColorMode } from "chains/editor/useColorMode";

const DEFAULT_DESCRIPTION = (
  <>
    <Text mb={2}>Click the connector to search for matching components.</Text>
    <Text>
      Attach components to this connector by dragging them from the search
      results in the left panel.
    </Text>
  </>
);

export const ConnectorPopover = ({
  type,
  node,
  connector,
  label,
  placement,
  children,
}) => {
  const { isOpen, onToggle, onClose } = useDisclosure();
  const { highlight, isLight } = useEditorColorMode();
  const { selectedConnector, setSelectedConnector } =
    useContext(SelectedNodeContext);

  const source_types = Array.isArray(connector.source_type)
    ? connector.source_type
    : [connector?.source_type];

  const description = connector.description || DEFAULT_DESCRIPTION;

  const onClick = useCallback(
    (event) => {
      // click: search for components
      // shift-click: toggle help
      const shiftKey = event.shiftKey;
      if (shiftKey) {
        onToggle();
      } else if (selectedConnector?.connector !== connector) {
        setSelectedConnector({ type, node, connector });
      } else {
        setSelectedConnector(null);
      }
    },
    [onToggle, selectedConnector]
  );

  const hover = isLight ? { color: "blue.400" } : { color: "blue.400" };

  return (
    <Popover
      isOpen={isOpen}
      onClose={onClose}
      placement={placement}
      closeOnBlur={true}
    >
      <PopoverTrigger>
        <Box
          as="button"
          onClick={onClick}
          title={"shift-click for help"}
          _hover={hover}
        >
          {children || label || connector.label || connector.key}
        </Box>
      </PopoverTrigger>
      <PopoverContent zIndex={99999} color={"white"}>
        <PopoverArrow />
        <PopoverHeader>
          {source_types?.map((type) => {
            return (
              <Badge px={2} mr={1} bg={highlight[type]} key={type}>
                {type}
              </Badge>
            );
          })}
        </PopoverHeader>
        <PopoverCloseButton />
        <PopoverBody>{description}</PopoverBody>
      </PopoverContent>
    </Popover>
  );
};

ConnectorPopover.defaultProps = {
  placement: "left",
};
