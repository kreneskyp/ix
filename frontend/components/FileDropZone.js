import React from "react";
import { Box, Text, useToast } from "@chakra-ui/react";
import { useUpload } from "hooks/useUpload";

const UploadProgressNotification = ({ progress }) => {
  return null;
};

const UploadSuccessNotification = ({ artifact }) => {
  return (
    <Box>
      <Text>Uploaded {artifact.name}</Text>
    </Box>
  );
};

export const FileDropZone = ({ task_id, children, ...props }) => {
  const toast = useToast();
  let toastId;

  const onStart = () => {
    toastId = toast({
      title: "Uploading...",
      description: <UploadProgressNotification progress={0} />,
      status: "info",
      duration: null,
      isClosable: true,
      position: "bottom-right",
    });
  };

  const onProgress = (percentCompleted) => {
    // Update the toast notification with the upload progress
    // XXX: This is not working because the server isn't responding with updates.
    //      Appears to be a nginx/fastapi config issue.
    toast.update(toastId, {
      description: <UploadProgressNotification progress={percentCompleted} />,
    });
  };

  const onSuccess = (artifact) => {
    toast.update(toastId, {
      title: "Upload successful",
      description: <UploadSuccessNotification artifact={artifact} />,
      status: "success",
      duration: 5000,
    });
  };

  const onError = (error) => {
    toast.update(toastId, {
      title: "Error uploading file",
      description: error.message,
      status: "error",
      duration: 10000,
    });
    setTimeout(() => {
      toast.close(toastId);
    }, 10000);
  };

  const { handleDragOver, handleDrop } = useUpload(task_id, {
    onSuccess,
    onProgress,
    onStart,
    onError,
  });

  return (
    <Box onDragOver={handleDragOver} onDrop={handleDrop} {...props}>
      {children}
    </Box>
  );
};
