import { useCallback } from "react";

export const useUpload = (
  task_id,
  { onSuccess, onProgress, onStart, onError }
) => {
  const uploadFile = useCallback(
    async (file) => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("task_id", task_id);

      if (onStart !== undefined) {
        onStart();
      }

      try {
        const response = await fetch("/api/upload/", {
          method: "POST",
          body: formData,
        });

        const contentLength = +response.headers.get("Content-Length");

        let receivedLength = 0;
        let chunks = [];

        const reader = response.body.getReader(); // Call getReader() only once

        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            break;
          }
          chunks.push(value);
          receivedLength += value.length;

          const percentCompleted = contentLength
            ? Math.round((receivedLength * 100) / contentLength)
            : 0;

          if (onProgress !== undefined) {
            onProgress(percentCompleted);
          }
        }

        let completeBlob = new Blob(chunks);
        const data = await completeBlob.text();
        const jsonData = JSON.parse(data);

        if (onSuccess !== undefined) {
          onSuccess(jsonData);
        }
      } catch (error) {
        console.log("Error uploading file:", error);
        if (onError !== undefined) {
          onError(error);
        }
      }
    },
    [task_id, onSuccess, onProgress, onStart, onError]
  );

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
  }, []);

  const handleDrop = useCallback(
    async (e) => {
      e.preventDefault();
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        await uploadFile(files[0]);
      }
    },
    [uploadFile]
  );

  return {
    handleDragOver,
    handleDrop,
    uploadFile,
  };
};
