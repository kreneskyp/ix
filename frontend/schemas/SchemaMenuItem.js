import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
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
import SchemaIcon from "icons/SchemaIcon";

export const SchemasMenuItem = ({ editor }) => {
  const { page, isLoading, load } = usePaginatedAPI("/api/schemas/", {
    loadDependencies: [location],
    limit: 90000,
    load: false,
  });

  return (
    <LeftMenuPopover onOpen={load}>
      <LeftSidebarPopupIcon>
        <MenuItem title="Schemas">
          <SchemaIcon />
        </MenuItem>
      </LeftSidebarPopupIcon>
      <LeftSidebarPopupHeader>
        <Flex width={"100%"} justifyContent={"space-between"}>
          <Text>Schemas</Text>
          <SchemaFormModalButton onSuccess={load}>
            <Button colorScheme="green" size={"xs"}>
              Add Schemas
            </Button>
          </SchemaFormModalButton>
        </Flex>
      </LeftSidebarPopupHeader>
      <LeftSidebarPopupContent width={800}>
        {isLoading ? (
          <Box
            height={"calc(100vh - 400px)"}
            width={500}
            display="flex"
            alignItems="center"
            justifyContent="center"
          >
            <Spinner size="xl" />
          </Box>
        ) : (
          <Box width={500}>
            <SchemaTable page={page} load={load} />
          </Box>
        )}
      </LeftSidebarPopupContent>
    </LeftMenuPopover>
  );
};

SchemasMenuItem.defaultProps = {
  editor: false,
};
