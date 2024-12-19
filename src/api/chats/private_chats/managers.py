from typing import Dict, Optional

from starlette.websockets import WebSocket


class PrivateConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}

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