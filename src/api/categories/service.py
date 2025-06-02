from typing import List, Tuple

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.database import get_async_session
from core.database.models import Category, News, User
from core.database.repositories import CategoryRepository

from .schemas import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    async def get_news_by_id(self, category_id: int) -> Category:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        return category

    async def get_all_categories(
        self, offset: int = 0, limit: int = 10
    ) -> Tuple[int, List[Category]]:
        return await self.repository.get_all(offset=offset, limit=limit)

    async def create_category(
        self, user: User, category_data: CategoryCreate
    ) -> Category:
        if not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin"
            )
        category_data_dict = category_data.model_dump()
        new_category = News(**category_data_dict)
        await self.repository.add(new_category)
        return new_category

    async def update_news(
        self,
        user: User,
        category: Category,
        category_data: CategoryUpdate,
    ) -> Category:
        if not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin"
            )
        category_data_dict = category_data.model_dump(
            exclude_unset=True, exclude_none=True
        )
        for key, value in category_data_dict.items():
            setattr(category, key, value)
        await self.repository.update(category)
        return category

    async def delete_category(self, user: User, category_id: int) -> None:
        if not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin"
            )
        category = await self.get_news_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="News not found"
            )
        await self.repository.delete(category)


def category_service_factory(
    session: AsyncSession = Depends(get_async_session),
) -> CategoryService:
    return CategoryService(CategoryRepository(session))
