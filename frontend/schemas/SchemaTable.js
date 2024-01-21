import React from "react";
import { Box, HStack, Text, VStack } from "@chakra-ui/react";
import { ModalTrigger } from "components/Modal";
import { SchemaFormModalButton } from "schemas/SchemaFormModalButton";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const SchemaTable = ({ type, page, Draggable, load }) => {
  const style = useEditorColorMode();

  return (
    <VStack alignItems={"start"} pt={2} px={2}>
      {page?.objects.map((schema, index) => (
        <HStack
          key={index}
          _hover={{ bg: "blackAlpha.300" }}
          height={75}
          borderRadius={5}
          width={"100%"}
        >
          <Box width={"100%"}>
            <SchemaFormModalButton schema={schema} type={type} onSuccess={load}>
              <ModalTrigger.Button>
                <HStack p={3}>
                  <Box>
                    <Text>{schema.name}</Text>
                    <Text {...style.help}>{schema.description}</Text>
                  </Box>
                </HStack>
              </ModalTrigger.Button>
            </SchemaFormModalButton>
          </Box>
          {Draggable && <Draggable schema={schema} />}
        </HStack>
      ))}
    </VStack>
  );
};
