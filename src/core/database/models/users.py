from sqlalchemy import BOOLEAN, VARCHAR, String, false
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TableNameMixin, str_128


class User(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        VARCHAR(128), unique=True, index=True, nullable=False
    )
    first_name: Mapped[str_128]
    last_name: Mapped[str_128]
    email: Mapped[str] = mapped_column(VARCHAR(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_superuser: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())
    is_teacher: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())
