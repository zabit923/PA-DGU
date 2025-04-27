from typing import Dict, Set

import socketio


class GroupSocketManager:
    def __init__(self, sio_server: socketio.AsyncServer):
        self.sio = sio_server
        self.rooms_users: Dict[int, Set[str]] = {}

    async def connect(self, sid: str, group_id: int, username: str):
        await self.sio.enter_room(sid, str(group_id))
        if group_id not in self.rooms_users:
            self.rooms_users[group_id] = set()
        self.rooms_users[group_id].add(username)

    async def disconnect(self, sid: str, group_id: int, username: str):
        await self.sio.leave_room(sid, str(group_id))
        if group_id in self.rooms_users:
            self.rooms_users[group_id].discard(username)
            if not self.rooms_users[group_id]:
                del self.rooms_users[group_id]

    async def send_message(
        self, group_id: int, event: str, data: dict, skip_sid: str = None
    ):
        await self.sio.emit(event, data, room=str(group_id), skip_sid=skip_sid)

    async def notify_typing(self, group_id: int, username: str, is_typing: bool):
        await self.sio.emit(
            "typing",
            {"username": username, "is_typing": is_typing},
            room=str(group_id),
        )

    def get_online_users(self, group_id: int) -> Set[str]:
        return self.rooms_users.get(group_id, set())
