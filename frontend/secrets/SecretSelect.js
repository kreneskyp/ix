import React from "react";
import { Box, HStack, Select, Tooltip } from "@chakra-ui/react";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlusCircle } from "@fortawesome/free-solid-svg-icons";
import SecretsFormModalButton from "secrets/SecretsFormModalButton";
import { ModalTriggerButton } from "components/Modal";

export const SecretSelect = ({ secretKey, value, onChange }) => {
  const style = useEditorColorMode();
  const { page, load, isLoading } = usePaginatedAPI("/api/secrets/", {
    limit: 1000,
    load: false,
  });

  React.useEffect(() => {
    load({ secret_type: secretKey }).catch((err) => {
      console.error("failed to load secrets", err);
    });
  }, [secretKey]);

  // New Secret callback: refresh secrets and select the new secret
  const loadAndSelect = (response) => {
    load({ secret_type: secretKey }).then(() => {
      onChange({
        target: {
          value: response.id,
        },
      });
    });
  };

  return (
    <HStack>
      <SecretsFormModalButton forType={secretKey} onSuccess={loadAndSelect}>
        <ModalTriggerButton>
          <Tooltip label="Add Secret">
            <Box
              color={"gray.500"}
              _hover={{ color: "green.400", bg: "transparent" }}
              mx={0}
            >
              <FontAwesomeIcon icon={faPlusCircle} />
            </Box>
          </Tooltip>
        </ModalTriggerButton>
      </SecretsFormModalButton>
      <Select
        value={value || ""}
        onChange={onChange}
        placeholder={"Select a secret"}
        {...style.input}
        ml={0}
      >
        {page?.objects?.map((secret) => (
          <option key={secret.id} value={secret.id}>
            {secret.name}
          </option>
        ))}
      </Select>
    </HStack>
  );
};
