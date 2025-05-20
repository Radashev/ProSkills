from fastapi import WebSocket
from typing import Dict, List, Set
import json



class WebSocketManager:
    def __init__(self):
        # Активные соединения (все подключенные клиенты)
        self.active_connections: List[WebSocket] = []
        
        # Словарь для хранения соединений по комнатам
        # Ключ = ID комнаты (например, "course_1"), Значение = список соединений
        self.room_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Принимает новое WebSocket соединение"""
        await websocket.accept()
        self.active_connections.append(websocket)
        return websocket
    
    def disconnect(self, websocket: WebSocket):
        """Обрабатывает отключение WebSocket"""
        # Удаляем из списка активных соединений
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Удаляем из всех комнат
        for room_id, connections in list(self.room_connections.items()):
            if websocket in connections:
                connections.remove(websocket)
                # Если комната пуста, удаляем её
                if not connections:
                    del self.room_connections[room_id]
    
    def join_room(self, websocket: WebSocket, room_id: str):
        """Добавляет соединение в комнату"""
        if room_id not in self.room_connections:
            self.room_connections[room_id] = []
        
        if websocket not in self.room_connections[room_id]:
            self.room_connections[room_id].append(websocket)
    
    def leave_room(self, websocket: WebSocket, room_id: str):
        """Удаляет соединение из комнаты"""
        if room_id in self.room_connections:
            if websocket in self.room_connections[room_id]:
                self.room_connections[room_id].remove(websocket)
            
            # Если комната пустая, удаляем её
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Отправляет сообщение конкретному соединению"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def broadcast(self, message: dict):
        """Отправляет сообщение всем подключенным клиентам"""
        disconnected = []
        
        for websocket in self.active_connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error broadcasting message: {e}")
                disconnected.append(websocket)
        
        # Удаляем разорванные соединения
        for websocket in disconnected:
            self.disconnect(websocket)
    
    
    async def broadcast_to_room(self, message: dict, room_id: str):
        "Send a message to everyone in the room"
        if room_id not in self.room_connections:
            return

        disconnected = []

        for websocket in self.room_connections[room_id]:
            try: 
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error sending message to room {room_id}: {e}")
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)
            
manager = WebSocketManager()