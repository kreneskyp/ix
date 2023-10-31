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

export const LangServerDeleteButton = ({ langserver, onSuccess }) => {
  const [isOpen, setIsOpen] = useState(false);
  const cancelRef = useRef();
  const url = `/api/langservers/${langserver?.id}`;
  const { call: deleteLangServer } = useDeleteAPI(url); // Assuming useDeleteAPI is a custom hook you've defined elsewhere

  const onClose = () => setIsOpen(false);
  const onDelete = () => {
    deleteLangServer().then(() => {
      onSuccess(); // Call the onSuccess handler passed via props
    });
    setIsOpen(false); // Close the dialog
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
              Delete Language Server
            </AlertDialogHeader>

            <AlertDialogBody>
              Are you sure you want to delete this language server? This action
              cannot be undone.
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
