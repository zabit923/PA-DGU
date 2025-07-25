from typing import List

from models import Category
from schemas import CategoryDataSchema, PaginationParams
from services.v1.base import BaseEntityManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class CategoryDataManager(BaseEntityManager[CategoryDataSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=CategoryDataSchema, model=Category)

    async def get_all_categories(
        self,
        pagination: PaginationParams,
    ) -> tuple[List[Category], int]:
        statement = select(self.model).distinct()
        return await self.get_paginated_items(statement, pagination)

    async def get_category_by_id(self, category_id: int) -> Category:
        statement = select(self.model).where(self.model.id == category_id)
        return await self.get_one(statement)
