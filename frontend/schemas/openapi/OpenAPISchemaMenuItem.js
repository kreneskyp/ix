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
import { OpenAPIIcon } from "icons/OpenAPIIcon";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { OpenAPIDraggable } from "schemas/openapi/OpenAPIDraggable";

export const OpenAPISchemaMenuItem = ({ editor }) => {
  const { page, isLoading, load } = usePaginatedAPI("/api/schemas/", {
    args: { type: "openapi" },
    loadDependencies: [location],
    limit: 90000,
    load: false,
  });
  const style = useEditorColorMode();

  return (
    <LeftMenuPopover onOpen={load}>
      <LeftSidebarPopupIcon>
        <MenuItem title="API Specs">
          <OpenAPIIcon {...style.menu_icon} />
        </MenuItem>
      </LeftSidebarPopupIcon>
      <LeftSidebarPopupHeader>
        <Flex width={"100%"} justifyContent={"space-between"}>
          <Text>OpenAPI Specs</Text>
          <SchemaFormModalButton onSuccess={load} type={"openapi"}>
            <Button colorScheme="green" size={"xs"}>
              Add Spec
            </Button>
          </SchemaFormModalButton>
        </Flex>
        <Text {...style.help}>
          API specifications connecting chains to remote services.
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
              type={"openapi"}
              Draggable={OpenAPIDraggable}
            />
          </Box>
        )}
      </LeftSidebarPopupContent>
    </LeftMenuPopover>
  );
};

OpenAPISchemaMenuItem.defaultProps = {
  editor: false,
};
