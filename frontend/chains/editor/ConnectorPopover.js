import React, { useState, useEffect, useContext } from "react";
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
} from "@chakra-ui/react";
import { SelectedNodeContext } from "chains/editor/SelectedNodeContext";
import { useEditorColorMode } from "chains/editor/useColorMode";

const DEFAULT_DESCRIPTION =
  "Attach components to this connector by dragging them from the search results in the left panel.";

export const ConnectorPopover = ({
  type,
  node,
  connector,
  label,
  placement,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const { highlight } = useEditorColorMode();
  const { setSelectedConnector } = useContext(SelectedNodeContext);

  useEffect(() => {
    if (isOpen) {
      setSelectedConnector({ type, node, connector });
    }
  }, [isOpen, setSelectedConnector, connector]);

  const openPopover = () => setIsOpen(true);
  const closePopover = () => setIsOpen(false);

  const source_types = Array.isArray(connector.source_type)
    ? connector.source_type
    : [connector?.source_type];

  const description = connector.description || DEFAULT_DESCRIPTION;

  return (
    <Popover
      isOpen={isOpen}
      onClose={closePopover}
      placement={placement || "left"}
    >
      <PopoverTrigger>
        <Box as="button" onClick={openPopover}>
          {label || connector.key}
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
        <PopoverCloseButton onClick={closePopover} />
        <PopoverBody>{description}</PopoverBody>
      </PopoverContent>
    </Popover>
  );
};
