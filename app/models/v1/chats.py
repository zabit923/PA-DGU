from typing import TYPE_CHECKING, List

from sqlalchemy import BOOLEAN, TEXT, Column, ForeignKey, Table, UniqueConstraint, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel

if TYPE_CHECKING:
    from app.models import Group, User


class PrivateRoom(BaseModel):
    __tablename__ = "private_rooms"

    messages: Mapped[List["PrivateMessage"]] = relationship(
        "PrivateMessage", back_populates="room", lazy="selectin", cascade="all, delete"
    )
    members: Mapped[List["User"]] = relationship(
        "User", secondary="room_members", back_populates="rooms", lazy="selectin"
    )


class GroupMessage(BaseModel):
    __tablename__ = "group_messages"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    text: Mapped[str] = mapped_column(TEXT, nullable=False)

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


class GroupMessageCheck(BaseModel):
    __tablename__ = "group_message_checks"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    message_id: Mapped[int] = mapped_column(
        ForeignKey("group_messages.id", ondelete="CASCADE"), nullable=False
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


class PrivateMessage(BaseModel):
    __tablename__ = "private_messages"

    room_id: Mapped[int] = mapped_column(ForeignKey(PrivateRoom.id), nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    text: Mapped[str] = mapped_column(TEXT, nullable=False)
    is_readed: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())

    sender: Mapped["User"] = relationship(
        "User", back_populates="sent_personal_messages", lazy="selectin"
    )
    room: Mapped["PrivateRoom"] = relationship(
        "PrivateRoom", back_populates="messages", lazy="selectin"
    )


room_members = Table(
    "room_members",
    BaseModel.metadata,
    Column("room_id", ForeignKey(PrivateRoom.id), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)
