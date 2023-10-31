import React from "react";
import { LangServerForm } from "langservers/LangServerForm";
import { ModalTrigger, ModalTriggerContent } from "components/Modal";
import { Box } from "@chakra-ui/react";

export const LangServerFormModalButton = ({
  langserver,
  onOpen,
  onSuccess,
  children,
}) => {
  return (
    <ModalTrigger
      onOpen={onOpen}
      showClose={false}
      size="xl"
      title="Edit LangServer"
    >
      {children}
      <ModalTriggerContent>
        <Box p={4}>
          <LangServerForm langserver={langserver} onSuccess={onSuccess} />
        </Box>
      </ModalTriggerContent>
    </ModalTrigger>
  );
};

export default LangServerFormModalButton;
