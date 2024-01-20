import React from "react";
import { Box, HStack, Select, Tooltip } from "@chakra-ui/react";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlusCircle } from "@fortawesome/free-solid-svg-icons";
import { ModalTriggerButton } from "components/Modal";
import SchemaFormModalButton from "schemas/SchemaFormModalButton";

export const SchemaSelect = ({ type, value, onChange }) => {
  const style = useEditorColorMode();
  const { page, load, isLoading } = usePaginatedAPI("/api/schemas/", {
    type: type,
    limit: 1000,
    load: false,
  });

  React.useEffect(() => {
    load({ type: type || "json" }).catch((err) => {
      console.error("failed to load schemas", err);
    });
  }, [type]);

  // New Schema callback: refresh schemas and select the new schema
  const loadAndSelect = (response) => {
    load({ type: type || "json" }).then(() => {
      onChange(response.id);
    });
  };

  const handleChange = (e) => {
    onChange(e.target.value);
  };

  return (
    <HStack>
      <SchemaFormModalButton forType={schemaKey} onSuccess={loadAndSelect}>
        <ModalTriggerButton>
          <Tooltip label="Add Schema">
            <Box
              color={"gray.500"}
              _hover={{ color: "green.400", bg: "transparent" }}
              mx={0}
            >
              <FontAwesomeIcon icon={faPlusCircle} />
            </Box>
          </Tooltip>
        </ModalTriggerButton>
      </SchemaFormModalButton>
      <Select
        value={value || ""}
        onChange={handleChange}
        placeholder={"Select a schema"}
        {...style.input}
        ml={0}
      >
        {page?.objects?.map((schema) => (
          <option key={schema.id} value={schema.id}>
            {schema.name}
          </option>
        ))}
      </Select>
    </HStack>
  );
};
