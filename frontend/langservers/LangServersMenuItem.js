import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faServer } from "@fortawesome/free-solid-svg-icons";
import { Box, Button, Flex, Text, Spinner } from "@chakra-ui/react";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";

import {
  LeftMenuPopover,
  LeftSidebarPopupContent,
  LeftSidebarPopupHeader,
  LeftSidebarPopupIcon,
} from "site/LeftMenuPopover";
import { LangServersTable } from "langservers/LangServersList";
import { LangServerFormModalButton } from "langservers/LangServerModalButton";

export const LangServersMenuItem = ({ editor }) => {
  const { page, isLoading, load } = usePaginatedAPI("/api/langservers/", {
    loadDependencies: [location],
    limit: 90000,
    load: false,
  });

  return (
    <LeftMenuPopover onOpen={load}>
      <LeftSidebarPopupIcon>
        <FontAwesomeIcon icon={faServer} />
      </LeftSidebarPopupIcon>
      <LeftSidebarPopupHeader>
        <Flex width={"100%"} justifyContent={"space-between"}>
          <Text>LangServers</Text>
          <LangServerFormModalButton onSuccess={load}>
            <Button colorScheme="green" size={"xs"}>
              Add LangServe
            </Button>
          </LangServerFormModalButton>
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
            <LangServersTable page={page} load={load} />
          </Box>
        )}
      </LeftSidebarPopupContent>
    </LeftMenuPopover>
  );
};

LangServersMenuItem.defaultProps = {
  editor: false,
};
