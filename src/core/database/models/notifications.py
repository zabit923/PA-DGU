from typing import TYPE_CHECKING

from sqlalchemy import BOOLEAN, TIMESTAMP, VARCHAR, ForeignKey, false, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base, TableNameMixin

if TYPE_CHECKING:
    from core.database.models import User


class Notification(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(VARCHAR(255))
    body: Mapped[str] = mapped_column(VARCHAR())
    is_read: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())
    created_at: Mapped[func.now()] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="notifications", lazy="selectin"
    )

    def __repr__(self):
        return f"{self.title} | {self.user}"
