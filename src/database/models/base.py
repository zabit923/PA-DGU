from datetime import datetime
from typing import Annotated

from sqlalchemy import VARCHAR, TIMESTAMP
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
    mapped_column,
    Mapped
)
from sqlalchemy.sql.functions import now


class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)


class TableNameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'


int_pk = Annotated[int, mapped_column(primary_key=True)]
str_20 = Annotated[str, mapped_column(VARCHAR(20))]
str_50 = Annotated[str, mapped_column(VARCHAR(50))]
str_128 = Annotated[str, mapped_column(VARCHAR(128))]
str_255 = Annotated[str, mapped_column(VARCHAR(255))]
str_500 = Annotated[str, mapped_column(VARCHAR(500))]
timestamp_now = Annotated[datetime, mapped_column(TIMESTAMP, server_default=now())]
