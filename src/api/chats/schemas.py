from typing import Optional

from pydantic import BaseModel


class GroupMessageCreateSchema(BaseModel):
    id: int
    text: Optional[str] = None
    group_id: int
    sender: int
