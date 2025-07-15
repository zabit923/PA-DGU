from typing import List, Tuple

from core.database.models import Category
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self, offset: int = 0, limit: int = 10
    ) -> Tuple[int, List[Category]]:
        total_stmt = select(func.count()).select_from(Category)
        total_result = await self.session.execute(total_stmt)
        total = total_result.scalar_one()

        statement = select(Category).offset(offset).limit(limit)
        result = await self.session.execute(statement)
        categories = result.scalars().all()
        return total, categories

    async def get_by_id(self, category_id: int) -> Category:
        statement = select(Category).where(Category.id == category_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def add(self, category: Category) -> None:
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)

    async def update(self, category: Category) -> None:
        await self.session.commit()
        await self.session.refresh(category)

    async def delete(self, category: Category) -> None:
        await self.session.delete(category)
        await self.session.commit()
