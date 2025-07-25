from typing import List, Tuple

from core.exceptions import CategoryNotFoundError
from models import Category
from schemas import CategoryResponseSchema, PaginationParams
from services.v1.base import BaseService
from services.v1.categories.data_manager import CategoryDataManager
from sqlalchemy.ext.asyncio import AsyncSession


class CategoryService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session)
        self.category_data_manager = CategoryDataManager(session)

    async def get_all_categories(
        self,
        pagination: PaginationParams,
    ) -> Tuple[List[Category], int]:
        categories, total = await self.category_data_manager.get_all_categories(
            pagination
        )
        return [
            CategoryResponseSchema.model_validate(category) for category in categories
        ], total

    async def get_category_by_id(self, category_id: int) -> Category:
        category = await self.category_data_manager.get_category_by_id(category_id)
        if not category:
            raise CategoryNotFoundError(detail="Группа не найдена")
        return category
