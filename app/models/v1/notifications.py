from typing import TYPE_CHECKING

from sqlalchemy import BOOLEAN, VARCHAR, ForeignKey, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel

if TYPE_CHECKING:
    from app.models import User


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(VARCHAR(255))
    body: Mapped[str] = mapped_column(VARCHAR())
    is_read: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())

    user: Mapped["User"] = relationship(
        "User", back_populates="notifications", lazy="selectin"
    )
