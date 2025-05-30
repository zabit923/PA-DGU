from typing import List, Tuple

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.database.models import News, User


class NewsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, offset: int = 0, limit: int = 10) -> Tuple[int, List[News]]:
        total_stmt = select(func.count()).select_from(News)
        total_result = await self.session.execute(total_stmt)
        total = total_result.scalar_one()

        statement = select(News).offset(offset).limit(limit)
        result = await self.session.execute(statement)
        news = result.scalars().all()
        return total, news

    async def get_by_id(self, news_id: int) -> News:
        statement = select(User).where(User.id == news_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def add(self, news: News) -> None:
        self.session.add(news)
        await self.session.commit()
        await self.session.refresh(news)

    async def update(self, news: News) -> None:
        await self.session.commit()
        await self.session.refresh(news)

    async def delete(self, news: News) -> None:
        await self.session.delete(news)
        await self.session.commit()
