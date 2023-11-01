import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faKey } from "@fortawesome/free-solid-svg-icons";
import { Box, Button, Flex, Text, Spinner } from "@chakra-ui/react";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";

import {
  LeftMenuPopover,
  LeftSidebarPopupContent,
  LeftSidebarPopupHeader,
  LeftSidebarPopupIcon,
} from "site/LeftMenuPopover";
import { SecretsTable } from "secrets/SecretsTable";
import { SecretsFormModalButton } from "secrets/SecretsFormModalButton";

export const SecretsMenuItem = ({ editor }) => {
  const { page, isLoading, load } = usePaginatedAPI("/api/secrets/", {
    loadDependencies: [location],
    limit: 90000,
    load: false,
  });

  return (
    <LeftMenuPopover onOpen={load}>
      <LeftSidebarPopupIcon>
        <FontAwesomeIcon icon={faKey} />
      </LeftSidebarPopupIcon>
      <LeftSidebarPopupHeader>
        <Flex width={"100%"} justifyContent={"space-between"}>
          <Text>Secrets</Text>
          <SecretsFormModalButton onSuccess={load}>
            <Button colorScheme="green" size={"xs"}>
              Add Secrets
            </Button>
          </SecretsFormModalButton>
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
            <SecretsTable page={page} load={load} />
          </Box>
        )}
      </LeftSidebarPopupContent>
    </LeftMenuPopover>
  );
};

SecretsMenuItem.defaultProps = {
  editor: false,
};
