import { useEffect, useRef, useCallback } from "react";

// Define message types with additional fields from the backend broadcast
export interface WebSocketMessage {
  command?: "join_room" | "leave_room" | "update_rating" | "create_review";
  event?:
    | "joined_room"
    | "left_room"
    | "rating_updated" // Event broadcast from backend after a rating update
    | "rating_confirmation"
    | "review_created"
    | "error";
  room_id?: string;
  rating?: number;
  course_id?: number;
  new_rating?: number;
  ratings_count?: number;
  review_id?: number;
  user_id?: string;
  data?: {
    room_id?: string;
    rating?: number;
    message?: string;
    status?: string;
  };
}

// Define hook return type
interface WebSocketHook {
  sendMessage: (message: WebSocketMessage) => void;
  joinRoom: (roomId: string) => void;
  leaveRoom: (roomId: string) => void;
  updateRating: (roomId: string, rating: number) => void;
  createReview: (roomId: string, courseId: number) => void;
  isConnected: boolean;
}

export const useWebSocket = (
  onMessage: (message: WebSocketMessage) => void
): WebSocketHook => {
  const ws = useRef<WebSocket | null>(null);
  const pending = useRef<WebSocketMessage[]>([]);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
  const isConnected = useRef<boolean>(false);

  const connect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = null;
    }

    const wsUrl = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";

    try {
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        // console.log("WebSocket Connected");
        isConnected.current = true;
        // Flush any messages queued before open
        pending.current.forEach((msg) => ws.current!.send(JSON.stringify(msg)));
        pending.current = [];
      };

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          // console.log("Received WebSocket message:", message);
          onMessage(message);
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      ws.current.onerror = (error) => {
        console.error("WebSocket Error:", error);
        isConnected.current = false;
      };

      ws.current.onclose = (event) => {
        // console.log("WebSocket Disconnected", event.code);
        isConnected.current = false;
        if (event.code !== 1000) {
          reconnectTimeout.current = setTimeout(connect, 5000);
        }
      };
    } catch (error) {
      console.error("Error creating WebSocket connection:", error);
      reconnectTimeout.current = setTimeout(connect, 5000);
    }
  }, [onMessage]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      ws.current?.close(1000, "Component unmounting");
    };
  }, [connect]);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      try {
        ws.current.send(JSON.stringify(message));
      } catch (error) {
        console.error("Error sending WebSocket message:", error);
      }
    } else {
      // Queue until connection opens
      pending.current.push(message);
    }
  }, []);

  const joinRoom = useCallback(
    (roomId: string) => {
      sendMessage({ command: "join_room", room_id: roomId });
    },
    [sendMessage]
  );

  const leaveRoom = useCallback(
    (roomId: string) => {
      sendMessage({ command: "leave_room", room_id: roomId });
    },
    [sendMessage]
  );

  const updateRating = useCallback(
    (roomId: string, rating: number) => {
      sendMessage({ command: "update_rating", room_id: roomId, rating });
    },
    [sendMessage]
  );

  const createReview = useCallback(
    (roomId: string, courseId: number) => {
      sendMessage({
        command: "create_review",
        room_id: roomId,
        course_id: courseId,
      });
    },
    [sendMessage]
  );

  return {
    sendMessage,
    joinRoom,
    leaveRoom,
    updateRating,
    createReview,
    isConnected: isConnected.current,
  };
};
