import React, { useEffect } from "react";
import { Box, Table, Thead, Tbody, Tr, Th, Td, Text } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTrash } from "@fortawesome/free-solid-svg-icons";

import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";
import CenteredSpinner from "site/CenteredSpinner";
import { ModalTrigger } from "components/Modal";
import { SCROLLBAR_CSS } from "site/css";
import { SecretsFormModalButton } from "secrets/SecretsFormModalButton";

export const SecretsTable = ({ page, load }) => {
  return (
    <Box p={0}>
      <Table variant="simple" m={0} p={0} display="block">
        <Thead display="table" width="100%">
          <Tr>
            <Th>Type</Th>
            <Th>Name</Th>
          </Tr>
        </Thead>
        <Box
          height={"calc(100vh - 400px)"}
          overflowY="auto"
          display="block"
          css={SCROLLBAR_CSS}
        >
          <Tbody display="table" width="100%">
            {page?.objects.map((secret, index) => (
              <Tr key={index}>
                <Td>{secret.type.name}</Td>
                <Td>
                  <SecretsFormModalButton secret={secret} onSuccess={load}>
                    <ModalTrigger.Button>{secret.name}</ModalTrigger.Button>
                  </SecretsFormModalButton>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Box>
      </Table>
    </Box>
  );
};
