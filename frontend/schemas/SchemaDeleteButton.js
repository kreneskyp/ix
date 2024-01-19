import React, { useRef, useState } from "react";
import {
  Button,
  AlertDialog,
  AlertDialogOverlay,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogBody,
  AlertDialogFooter,
} from "@chakra-ui/react";
import { useDeleteAPI } from "utils/hooks/useDeleteAPI";

export const SchemaDeleteButton = ({ schema, onSuccess }) => {
  const [isOpen, setIsOpen] = useState(false);
  const cancelRef = useRef();
  const url = `/api/schemas/${schema?.id}`;
  const { call: deleteSchema } = useDeleteAPI(url);

  const onClose = () => setIsOpen(false);
  const onDelete = () => {
    deleteSchema().then(() => {
      onSuccess();
    });
    setIsOpen(false);
  };

  return (
    <>
      <Button colorScheme="red" onClick={() => setIsOpen(true)}>
        Delete
      </Button>

      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete Schema
            </AlertDialogHeader>

            <AlertDialogBody>
              Are you sure you want to delete this schema? This action cannot be
              undone.
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onClose}>
                Cancel
              </Button>
              <Button colorScheme="red" onClick={onDelete} ml={3}>
                Delete
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </>
  );
};
