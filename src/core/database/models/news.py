from datetime import datetime
from typing import Optional

from sqlalchemy import TEXT, TIMESTAMP, VARCHAR, String, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database.models import Base, TableNameMixin


class News(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    text: Mapped[str] = mapped_column(TEXT, nullable=False)
    image: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"{self.title} | {self.created_at}"
