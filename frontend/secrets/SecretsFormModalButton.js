import React from "react";
import { SecretsForm } from "secrets/SecretsForm";
import { ModalTrigger, ModalTriggerContent } from "components/Modal";
import { Box } from "@chakra-ui/react";

export const SecretsFormModalButton = ({
  forType,
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
      closeOnBlur={false}
    >
      {children}
      <ModalTriggerContent>
        <Box p={4}>
          <SecretsForm
            forType={forType}
            secret={secret}
            onSuccess={onSuccess}
          />
        </Box>
      </ModalTriggerContent>
    </ModalTrigger>
  );
};

export default SecretsFormModalButton;
