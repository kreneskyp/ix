import React, { useEffect } from "react";
import { Box, Table, Thead, Tbody, Tr, Th, Td, Text } from "@chakra-ui/react";

import { LangServerFormModalButton } from "langservers/LangServerModalButton";
import { ModalTrigger } from "components/Modal";
import { SCROLLBAR_CSS } from "site/css";

export const LangServersTable = ({ page, load }) => {
  return (
    <Box p={0}>
      <Table variant="simple" m={0} p={0} display="block">
        <Thead display="table" width="100%">
          <Tr>
            <Th>Name</Th>
            <Th>Description</Th>
            <Th></Th>
          </Tr>
        </Thead>
        <Box
          height={"calc(100vh - 400px)"}
          overflowY="auto"
          display="block"
          css={SCROLLBAR_CSS}
        >
          <Tbody display="table" width="100%">
            {page?.objects.map((langserver, index) => (
              <Tr key={index}>
                <Td>
                  <LangServerFormModalButton
                    langserver={langserver}
                    onSuccess={load}
                  >
                    <ModalTrigger.Button>
                      <Text cursor={"pointer"} _hover={{ color: "blue.400" }}>
                        {langserver.name}
                      </Text>
                    </ModalTrigger.Button>
                  </LangServerFormModalButton>
                </Td>
                <Td>{langserver.description}</Td>
                <Td></Td>
              </Tr>
            ))}
          </Tbody>
        </Box>
      </Table>
    </Box>
  );
};
