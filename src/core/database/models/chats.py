from typing import TYPE_CHECKING, List

from sqlalchemy import BOOLEAN, TEXT, TIMESTAMP, Column, ForeignKey, Table, false, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base, TableNameMixin

if TYPE_CHECKING:
    from core.database.models import Group, User


class PrivateRoom(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[func.now()] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    messages: Mapped[List["PrivateMessage"]] = relationship(
        "PrivateMessage", back_populates="room", lazy="selectin", cascade="all, delete"
    )
    members: Mapped[List["User"]] = relationship(
        "User", secondary="room_members", back_populates="rooms", lazy="selectin"
    )

    def __repr__(self):
        return f"{self.members}"


class GroupMessage(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    text: Mapped[str] = mapped_column(TEXT, nullable=False)
    created_at: Mapped[func.now()] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    sender: Mapped["User"] = relationship(
        "User", back_populates="sent_group_messages", lazy="selectin"
    )
    group: Mapped["Group"] = relationship(
        "Group", back_populates="group_messages", lazy="selectin"
    )

    def __repr__(self):
        return f"Сообщение от: {self.sender}"


class PrivateMessage(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey(PrivateRoom.id), nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    text: Mapped[str] = mapped_column(TEXT, nullable=False)
    is_readed: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())
    created_at: Mapped[func.now()] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    sender: Mapped["User"] = relationship(
        "User", back_populates="sent_personal_messages", lazy="selectin"
    )
    room: Mapped["PrivateRoom"] = relationship(
        "PrivateRoom", back_populates="messages", lazy="selectin"
    )

    def __repr__(self):
        return f"Сообщение от: {self.sender}"


room_members = Table(
    "room_members",
    Base.metadata,
    Column("room_id", ForeignKey(PrivateRoom.id), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)
