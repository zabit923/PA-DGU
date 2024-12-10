from typing import Dict, List

from starlette.websockets import WebSocket


class GroupConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, group_id: int, websocket: WebSocket):
        await websocket.accept()
        if group_id not in self.active_connections:
            self.active_connections[group_id] = []
        self.active_connections[group_id].append(websocket)

    def disconnect(self, group_id: int, websocket: WebSocket):
        if group_id in self.active_connections:
            self.active_connections[group_id].remove(websocket)
            if not self.active_connections[group_id]:
                del self.active_connections[group_id]

    async def broadcast(self, group_id: int, message: str):
        if group_id in self.active_connections:
            for connection in self.active_connections[group_id]:
                await connection.send_text(message)
