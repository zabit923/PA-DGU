from typing import Optional

from pydantic import BaseModel


class MessageSchema(BaseModel):
    recipient: Optional[str]
    message: str
