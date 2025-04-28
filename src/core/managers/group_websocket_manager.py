from typing import Dict, Optional

from starlette.websockets import WebSocket


class GroupConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
        self.typing_status: Dict[int, Dict[str, bool]] = {}

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

    async def notify_deletion(self, group_id: int, message_id: int):
        if group_id in self.active_connections:
            for username, connection in self.active_connections[group_id].items():
                await connection.send_json(
                    {"action": "delete_message", "message_id": message_id}
                )

    async def notify_update(self, group_id: int, message_id: int):
        if group_id in self.active_connections:
            for username, connection in self.active_connections[group_id].items():
                await connection.send_json(
                    {"action": "update_message", "message_id": message_id}
                )

    async def notify_typing_status(self, group_id: int, username: str, is_typing: bool):
        if group_id not in self.typing_status:
            self.typing_status[group_id] = {}

        self.typing_status[group_id][username] = is_typing

        if group_id in self.active_connections:
            for username, connection in self.active_connections[group_id].items():
                await connection.send_json(
                    {"action": "typing", "username": username, "is_typing": is_typing}
                )

    @staticmethod
    async def send_error(message: str, websocket: WebSocket):
        await websocket.send_json({"status": "error", "message": message})


async def get_group_websocket_manager() -> GroupConnectionManager:
    return GroupConnectionManager()
