from typing import List, Optional

from models import News
from schemas import NewsCreateSchema, NewsDataSchema, NewsUpdateSchema, PaginationParams
from services.v1.base import BaseEntityManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class NewsDataManager(BaseEntityManager[NewsDataSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=NewsDataSchema, model=News)

    async def get_all_news(
        self,
        pagination: PaginationParams,
        category_id: Optional[int] = None,
        search: str = None,
    ) -> tuple[List[News], int]:
        statement = select(self.model).distinct()
        if search:
            statement = statement.filter(self.model.title.ilike(f"%{search}%"))
        if category_id:
            statement = statement.filter(self.model.category_id == category_id)
        return await self.get_paginated_items(statement, pagination)

    async def get_news_by_id(self, news_id: int) -> News:
        statement = select(self.model).where(self.model.id == news_id)
        return await self.get_one(statement)

    async def create_news(self, data: NewsCreateSchema, image_url: str) -> News:
        news_model = News(
            title=data.title,
            text=data.text,
            time_to_read=data.time_to_read,
            category_id=data.category_id,
            image=image_url,
        )
        return await self.add_one(news_model)

    async def update_news(
        self,
        news: News,
        data: NewsUpdateSchema,
        image_url: Optional[str] = None,
    ) -> News:
        if data.title:
            news.title = data.title
        if data.text:
            news.text = data.text
        if data.time_to_read:
            news.time_to_read = data.time_to_read
        if data.category_id:
            news.category_id = data.category_id
        if image_url:
            news.file = image_url
        return await self.update_one(news)
