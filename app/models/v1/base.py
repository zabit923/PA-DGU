from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Type, TypeVar, Union

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

T = TypeVar("T", bound="BaseModel")


class BaseModel(DeclarativeBase):

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    metadata = MetaData()

    @classmethod
    def table_name(cls) -> str:
        return cls.__tablename__

    @classmethod
    def fields(cls: Type[T]) -> List[str]:
        return cls.__mapper__.selectable.c.keys()

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"

    @staticmethod
    def dict_to_list_field(dict_field: Dict[str, Any]) -> List[str]:
        if not dict_field:
            return []
        return [k for k, v in dict_field.items() if v]

    @staticmethod
    def list_to_dict_field(list_field: Union[List[str], Set[str]]) -> Dict[str, bool]:
        if not list_field:
            return {}
        return {str(item): True for item in list_field}
