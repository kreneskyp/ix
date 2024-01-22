import React from "react";
import { Box, Button, Flex, Text, Spinner } from "@chakra-ui/react";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";

import {
  LeftMenuPopover,
  LeftSidebarPopupContent,
  LeftSidebarPopupHeader,
  LeftSidebarPopupIcon,
} from "site/LeftMenuPopover";
import { SchemaTable } from "schemas/SchemaTable";
import { SchemaFormModalButton } from "schemas/SchemaFormModalButton";
import { MenuItem } from "site/MenuItem";
import { JSONSchemaIcon } from "icons/JSONSchemaIcon";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { JSONSchemaDraggable } from "schemas/json/JSONSchemaDraggable";

export const JSONSchemaMenuItem = ({ editor }) => {
  const style = useEditorColorMode();
  const { page, isLoading, load } = usePaginatedAPI("/api/schemas/", {
    args: { type: "json" },
    loadDependencies: [location],
    limit: 90000,
    load: false,
  });

  return (
    <LeftMenuPopover onOpen={load}>
      <LeftSidebarPopupIcon>
        <MenuItem title="Schemas">
          <JSONSchemaIcon {...style.menu_icon} />
        </MenuItem>
      </LeftSidebarPopupIcon>
      <LeftSidebarPopupHeader>
        <Flex width={"100%"} justifyContent={"space-between"}>
          <Text>Schemas</Text>
          <SchemaFormModalButton onSuccess={load} type={"json"}>
            <Button colorScheme="green" size={"xs"}>
              Add Schema
            </Button>
          </SchemaFormModalButton>
        </Flex>
        <Text {...style.help}>
          JSON Schemas defining data types for data extraction & generation.
        </Text>
      </LeftSidebarPopupHeader>
      <LeftSidebarPopupContent width={800}>
        {isLoading ? (
          <Box
            height={"200px"}
            width={500}
            display="flex"
            alignItems="center"
            justifyContent="center"
          >
            <Spinner size="xl" />
          </Box>
        ) : (
          <Box width={500}>
            <SchemaTable
              page={page}
              load={load}
              type={"json"}
              Draggable={JSONSchemaDraggable}
            />
          </Box>
        )}
      </LeftSidebarPopupContent>
    </LeftMenuPopover>
  );
};

JSONSchemaMenuItem.defaultProps = {
  editor: false,
};
