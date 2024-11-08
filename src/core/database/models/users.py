from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import BOOLEAN, VARCHAR, false
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TableNameMixin, str_128

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class User(TableNameMixin, Base, SQLAlchemyBaseUserTable[int]):
    username: Mapped[str] = mapped_column(
        VARCHAR(128), unique=True, index=True, nullable=False
    )
    first_name: Mapped[str_128]
    last_name: Mapped[str_128]
    is_teacher: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, User)
