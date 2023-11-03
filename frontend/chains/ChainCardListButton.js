import React from "react";
import { Box, IconButton, SimpleGrid } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChain } from "@fortawesome/free-solid-svg-icons";

import { ModalTrigger } from "components/Modal";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";
import {
  useEditorColorMode,
  useSideBarColorMode,
} from "chains/editor/useColorMode";
import ChainCard from "chains/ChainCard";

const ChainCardList = ({ chains, Card }) => {
  const { scrollbar } = useEditorColorMode();
  return (
    <Box
      maxH="calc(100vh - 275px)"
      overflowY="auto"
      spacing={5}
      css={scrollbar}
      px={3}
    >
      <SimpleGrid columns={[1, 2, 3]} spacing="20px" minChildWidth="360px">
        {chains?.map((chain) => (
          <Card chain={chain} key={chain.id} />
        ))}
      </SimpleGrid>
    </Box>
  );
};

export const ChainCardListButton = ({ Card }) => {
  const style = useSideBarColorMode();
  const { page, load } = usePaginatedAPI("/api/chains/", {
    limit: 1000,
    load: false,
    args: { is_agent: false },
  });

  return (
    <ModalTrigger onOpen={load} title={"Chains"}>
      <IconButton
        icon={<FontAwesomeIcon icon={faChain} />}
        title={"Chains"}
        {...style.button}
      />
      <ModalTrigger.Content title="Manage Chains">
        <ChainCardList chains={page?.objects} Card={ChainCard} />
      </ModalTrigger.Content>
    </ModalTrigger>
  );
};
