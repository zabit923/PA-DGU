from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    BOOLEAN,
    TEXT,
    TIMESTAMP,
    Column,
    ForeignKey,
    Table,
    UniqueConstraint,
    false,
    func,
)
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
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.timezone("UTC+3", func.now()), nullable=False
    )

    sender: Mapped["User"] = relationship(
        "User", back_populates="sent_group_messages", lazy="selectin"
    )
    group: Mapped["Group"] = relationship(
        "Group", back_populates="group_messages", lazy="selectin"
    )
    users_who_checked: Mapped[List["GroupMessageCheck"]] = relationship(
        "GroupMessageCheck",
        back_populates="message",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"Сообщение от: {self.sender}"


class GroupMessageCheck(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    message_id: Mapped[int] = mapped_column(
        ForeignKey("groupmessages.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.timezone("UTC+3", func.now()), nullable=False
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="checked_messages", lazy="selectin"
    )
    message: Mapped["GroupMessage"] = relationship(
        "GroupMessage",
        back_populates="users_who_checked",
        lazy="selectin",
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "message_id", name="uq_user_message_check"),
    )

    def __repr__(self):
        return f"{self.user} | {self.created_at}"


class PrivateMessage(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey(PrivateRoom.id), nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    text: Mapped[str] = mapped_column(TEXT, nullable=False)
    is_readed: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.timezone("UTC+3", func.now()), nullable=False
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
