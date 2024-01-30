import React from "react";
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

export const DeleteButton = ({
  item,
  onSuccess,
  deleteUrl,
  confirmationMessage,
  itemName,
}) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const cancelRef = React.useRef();
  const url = deleteUrl || `/api/items/${item?.id}`;
  const { call: deleteItem } = useDeleteAPI(url);

  const onClose = () => setIsOpen(false);
  const onDelete = () => {
    deleteItem().then(() => {
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
              Delete {itemName || "Item"}
            </AlertDialogHeader>

            <AlertDialogBody>
              {confirmationMessage ||
                `Are you sure you want to delete this item? This action cannot be undone.`}
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
