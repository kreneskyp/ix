import { useState, useEffect } from "react";
import { useWebSocket } from "../websocket/WebSocketContext";

const useTaskLogNotifier = () => {
  const [taskLog, setTaskLog] = useState([]);
  const socket = useWebSocket();

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      const data = JSON.parse(event.data);
      setTaskLog((prevLog) => [...prevLog, data]);
    };

    socket.addEventListener("message", handleMessage);

    return () => {
      socket.removeEventListener("message", handleMessage);
    };
  }, [socket]);

  const sendUserResponse = (response) => {
    if (socket) {
      socket.send(JSON.stringify({ response }));
    }
  };

  return {
    taskLog,
    sendUserResponse,
  };
};

export default useTaskLogNotifier;
