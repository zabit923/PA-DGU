from datetime import datetime
from typing import Annotated

from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, declared_attr, mapped_column
from sqlalchemy.sql.functions import now


class Base(DeclarativeBase):
    __abstract__ = True


class TableNameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"


timestamp_now = Annotated[datetime, mapped_column(TIMESTAMP, server_default=now())]
