import React, { useEffect } from "react";
import {
  Box,
  HStack,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Text,
} from "@chakra-ui/react";
import { ModalTrigger } from "components/Modal";
import { SchemaFormModalButton } from "schemas/SchemaFormModalButton";
import { StyledIcon } from "components/StyledIcon";
import { SCHEMA_TYPE_OPTIONS } from "schemas/SchemaTypeSelect";

export const get_option = (value) => {
  const option = SCHEMA_TYPE_OPTIONS.find((option) => option.value === value);
  return option;
};

export const SchemaTable = ({ page, load }) => {
  return (
    <Box p={0}>
      <Table variant="simple" m={0} p={0} display="block">
        <Thead display="table" width="100%">
          <Tr>
            <Th>Type</Th>
            <Th>Name</Th>
          </Tr>
        </Thead>

        <Tbody display="table" width="100%">
          {page?.objects.map((schema, index) => (
            <Tr key={index}>
              <Td>
                <HStack>
                  <StyledIcon style={get_option(schema.type).icon} />
                  <Text>{get_option(schema.type).label}</Text>
                </HStack>
              </Td>
              <Td>
                <SchemaFormModalButton schema={schema} onSuccess={load}>
                  <ModalTrigger.Button>
                    <Text _hover={{ color: "blue.300" }}>{schema.name}</Text>
                  </ModalTrigger.Button>
                </SchemaFormModalButton>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};
