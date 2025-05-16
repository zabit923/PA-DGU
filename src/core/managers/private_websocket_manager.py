from datetime import datetime
from typing import Dict, Optional

from starlette.websockets import WebSocket


class PrivateConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
        self.typing_status: Dict[int, Dict[str, bool]] = {}

    async def connect(self, room_id: int, username: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][username] = websocket

    def disconnect(self, room_id: int, username: str):
        if room_id in self.active_connections:
            user_connections = self.active_connections[room_id]
            if username in user_connections:
                del user_connections[username]
                if not user_connections:
                    del self.active_connections[room_id]

    async def send_message(
        self, room_id: int, message: dict, exclude: Optional[str] = None
    ):
        if room_id in self.active_connections:
            for username, connection in self.active_connections[room_id].items():
                if username == exclude:
                    continue
                await connection.send_json(message)

    async def notify_deletion(self, room_id: int, message_id: int):
        if room_id in self.active_connections:
            for username, connection in self.active_connections[room_id].items():
                await connection.send_json(
                    {"action": "delete_message", "message_id": message_id}
                )

    async def notify_update(
        self, room_id: int, message_id: int, message_text: str, created_at: datetime
    ):
        if room_id in self.active_connections:
            for username, connection in self.active_connections[room_id].items():
                await connection.send_json(
                    {
                        "action": "update_message",
                        "message_id": message_id,
                        "text": message_text,
                        "created_at": created_at.isoformat(),
                    }
                )

    async def notify_typing_status(self, room_id: int, username: str, is_typing: bool):
        if room_id not in self.typing_status:
            self.typing_status[room_id] = {}
        self.typing_status[room_id][username] = is_typing
        if room_id in self.active_connections:
            for username, connection in self.active_connections[room_id].items():
                await connection.send_json(
                    {"action": "typing", "username": username, "is_typing": is_typing}
                )

    @staticmethod
    async def send_error(message: str, websocket: WebSocket):
        await websocket.send_json({"status": "error", "message": message})
