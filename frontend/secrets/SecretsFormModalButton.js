import React from "react";
import { SecretsForm } from "secrets/SecretsForm";
import { ModalTrigger, ModalTriggerContent } from "components/Modal";
import { Box } from "@chakra-ui/react";

export const SecretsFormModalButton = ({
  secret,
  onOpen,
  onSuccess,
  children,
}) => {
  return (
    <ModalTrigger
      onOpen={onOpen}
      showClose={false}
      size="xl"
      title="Edit Secret"
    >
      {children}
      <ModalTriggerContent>
        <Box p={4}>
          <SecretsForm secret={secret} onSuccess={onSuccess} />
        </Box>
      </ModalTriggerContent>
    </ModalTrigger>
  );
};

export default SecretsFormModalButton;
