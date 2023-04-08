import React, { createContext, useContext, useEffect, useState } from "react";

const WebSocketContext = createContext(null);

export const useWebSocket = () => {
  return useContext(WebSocketContext);
};

export const WebSocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const ws = new WebSocket(
      "ws://" + window.location.host + "/ws/check_task_status/"
    );
    setSocket(ws);

    ws.onopen = () => {
      console.log("WebSocket connection opened");
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed");
    };

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  return (
    <WebSocketContext.Provider value={socket}>
      {children}
    </WebSocketContext.Provider>
  );
};
