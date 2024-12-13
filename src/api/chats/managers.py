from typing import Dict, Optional

from starlette.websockets import WebSocket


class GroupConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}

    async def connect(self, group_id: int, username: str, websocket: WebSocket):
        await websocket.accept()
        if group_id not in self.active_connections:
            self.active_connections[group_id] = {}
        self.active_connections[group_id][username] = websocket

    def disconnect(self, group_id: int, username: str):
        if group_id in self.active_connections:
            user_connections = self.active_connections[group_id]
            if username in user_connections:
                del user_connections[username]
                if not user_connections:
                    del self.active_connections[group_id]

    async def broadcast(
        self, group_id: int, message: dict, exclude: Optional[str] = None
    ):
        if group_id in self.active_connections:
            for username, connection in self.active_connections[group_id].items():
                if username == exclude:
                    continue
                await connection.send_json(message)
