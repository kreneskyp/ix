import React from "react";
import { Select } from "@chakra-ui/react";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const SecretSelect = ({ secretKey, value, onChange }) => {
  const style = useEditorColorMode();
  const { page, load, isLoading } = usePaginatedAPI("/api/secrets/", {
    limit: 1000,
    load: false,
  });

  React.useEffect(() => {
    load({ secret_type: secretKey });
  }, [secretKey]);

  return (
    <Select
      value={value || ""}
      onChange={onChange}
      placeholder={"Select a secret"}
      {...style.input}
    >
      {page?.objects?.map((secret) => (
        <option key={secret.id} value={secret.id}>
          {secret.name}
        </option>
      ))}
    </Select>
  );
};
