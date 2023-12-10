import React from "react";
import { Box, SimpleGrid } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAddressBook } from "@fortawesome/free-solid-svg-icons";

import { ModalTrigger } from "components/Modal";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { MenuItem } from "site/MenuItem";

const AgentCardList = ({ agents, Card }) => {
  const { scrollbar } = useEditorColorMode();
  return (
    <Box
      maxH="calc(100vh - 275px)"
      overflowY="auto"
      spacing={5}
      css={scrollbar}
      px={3}
    >
      <SimpleGrid
        columns={[1, 2, 3]} // Responsive column setup
        spacing="20px"
        minChildWidth="360px" // Minimum width for each grid item
      >
        {agents?.map((agent) => (
          <Card agent={agent} key={agent.id} />
        ))}
      </SimpleGrid>
    </Box>
  );
};

export const AgentCardListButton = ({ Card }) => {
  const { page, load } = usePaginatedAPI("/api/agents/", {
    limit: 1000,
    load: false,
  });

  return (
    <ModalTrigger onOpen={load} title={"Agents"}>
      <MenuItem title={"Assistants"}>
        <FontAwesomeIcon icon={faAddressBook} />
      </MenuItem>
      <ModalTrigger.Content title="Manage Agents">
        <AgentCardList agents={page?.objects} Card={Card} />
      </ModalTrigger.Content>
    </ModalTrigger>
  );
};
